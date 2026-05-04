import unittest
import helics as h
import json
from datetime import datetime, timezone, timedelta
from dots_infrastructure.DataClasses import SimulatorConfiguration, TimeStepInformation
from esdl.esdl_handler import EnergySystemHandler
from dots_infrastructure import CalculationServiceHelperFunctions
import sys
import os
from unittest.mock import MagicMock

current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', 'src', 'RenewableService'))
sys.path.append(src_path)

# -----------------------------------------------------------------------------
# 1. Attempt to import your actual service. 
# -----------------------------------------------------------------------------
try:
    from renewableservice import RenewableService
except ImportError as e:
    print(f"❌ Failed to import service: {e}")
    RenewableService = None

# -----------------------------------------------------------------------------
# 2. Test Configuration
# -----------------------------------------------------------------------------
BROKER_TEST_PORT = 23406
START_DATE_TIME = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
SIMULATION_DURATION_IN_SECONDS = 3600

class TestRenewableService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Runs once before all tests: Spins up a local HELICS broker."""
        init_string = f"-f 1 --name=mainbroker --port={BROKER_TEST_PORT}"
        cls.broker = h.helicsCreateBroker("zmq", "", init_string)
        assert h.helicsBrokerIsConnected(cls.broker), "Failed to start local test broker!"

    @classmethod
    def tearDownClass(cls):
        """Runs once after all tests: Safely shuts down the HELICS broker."""
        h.helicsBrokerDisconnect(cls.broker)
        h.helicsBrokerFree(cls.broker)
        h.helicsCloseLibrary()

    def setUp(self):
        """Runs before each individual test."""
        if RenewableService is None:
            self.fail("RenewableService could not be imported. Fix your import statements first!")

        # Load your actual ESDL file first to get IDs
        self.esh = EnergySystemHandler()
        try:
            esdl_path = os.path.join(current_dir, "datacenter_bess_scenario.esdl")
            self.esh.load_file(esdl_path) 
            self.energy_system = self.esh.get_energy_system()
        except Exception as e:
            self.fail(f"Could not load ESDL file from {esdl_path}: {e}")

        # Dynamically find all PVInstallation IDs
        from esdl import esdl as esdl_types
        pvs = [obj.id for obj in self.energy_system.eAllContents() if isinstance(obj, esdl_types.PVInstallation)]
        if not pvs:
            self.fail("No PVInstallation assets found in the test ESDL!")
        self.test_esdl_id = pvs[0]

        # Inject the mock configuration with dynamic IDs
        def dynamic_mock_config():
            return SimulatorConfiguration(
                "RenewableService",                  # name
                pvs,                                 # esdl_ids
                "Mock-Renewable-Federate",           # federate_name
                "127.0.0.1",                         # broker_ip
                BROKER_TEST_PORT,                    # broker_port
                "local-test-sim",                    # simulation_id
                SIMULATION_DURATION_IN_SECONDS,      # simulation_duration
                START_DATE_TIME,                     # calculation_start_datetime
                "localhost",                         # influxdb_host
                "8086",                              # influxdb_port
                "admin",                             # influxdb_username
                "admin",                             # influxdb_password
                "GO-e",                              # influxdb_database_name
                h.HelicsLogLevel.DEBUG,              # log_level
                ["PVInstallation"]                   # registered_esdl_classes
            )
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = dynamic_mock_config

        # K8s Env Vars for InfluxDB
        os.environ['INFLUXDB_HOST'] = 'localhost'
        os.environ['INFLUXDB_PORT'] = '8086'
        os.environ['INFLUXDB_USER'] = 'admin'
        os.environ['INFLUXDB_PASSWORD'] = 'admin'
        os.environ['INFLUXDB_NAME'] = 'GO-e'

        self.service = RenewableService()

    def test_1_service_instantiation(self):
        """Tests if the service can initialize and connect to HELICS."""
        self.assertIsNotNone(self.service, "Service instantiated but returned None")
        print("\n✅ Renewable Service instantiated successfully!")

    def test_2_initialization(self):
        """Tests ESDL parsing and internal structures."""
        self.service.init_calculation_service(self.energy_system)
        self.assertIn(self.test_esdl_id, self.service.pv_properties)
        props = self.service.pv_properties[self.test_esdl_id]
        self.assertGreater(props["capacity_w"], 0)
        self.assertGreater(props["surface_area"], 0)
        print(f"\n✅ PV Asset {self.test_esdl_id} initialized with {props['capacity_w']/1e3}kW capacity.")

    def test_3_production_calculation(self):
        """Tests the physics-based production calculation."""
        self.service.init_calculation_service(self.energy_system)
        
        # Test night (irradiance = 0)
        prod_night = self.service.calculate_production_w(self.test_esdl_id, 0.0)
        self.assertEqual(prod_night, 0.0)

        # Test peak sun (irradiance = 1000)
        prod_peak = self.service.calculate_production_w(self.test_esdl_id, 1000.0)
        self.assertGreater(prod_peak, 0.0)
        
        # Should be roughly capacity_w (within 2% noise)
        cap = self.service.pv_properties[self.test_esdl_id]["capacity_w"]
        self.assertLess(prod_peak, cap * 1.05)
        print(f"\n✅ Production calculation verified: 0W at night, {prod_peak/1e3:.1f}kW at peak sun.")

    def test_4_day_ahead_renewables(self):
        """Verifies the Day-Ahead JSON generation."""
        self.service.init_calculation_service(self.energy_system)
        
        # Mock telemetry
        self.service.influx_connector.set_time_step_data_point = MagicMock()
        mock_time_step = MagicMock()

        test_time = START_DATE_TIME
        out = self.service.day_ahead_renewables(
            param_dict={}, simulation_time=test_time, 
            time_step_number=mock_time_step, esdl_id=self.test_esdl_id, energy_system=self.energy_system
        )
        
        self.assertNotEqual(out.planned_generation_DA, "")
        data = json.loads(out.planned_generation_DA)
        self.assertEqual(len(data["generation_w"]), 96)
        print("\n✅ Day-ahead renewable forecast generated 96 steps.")

if __name__ == '__main__':
    unittest.main(failfast=False)
