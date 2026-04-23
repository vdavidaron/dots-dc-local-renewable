<?xml version='1.0' encoding='UTF-8'?>
<esdl:EnergySystem xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:esdl="http://www.tno.nl/esdl" id="b9ea1ece-e2c8-4718-9e29-7a568a03fa27" name="Datacenter_BESS_Scenario" description="Datacenter with BESS and grid connection">
  <instance xsi:type="esdl:Instance" name="scenario_instance" id="2596ca78-275a-4d90-a205-710eca10d4e2">
    <area xsi:type="esdl:Area" name="Datacenter_Site" id="ed1f17a8-da15-41e1-b4d1-e5f7fbbb5f89">
      <asset xsi:type="esdl:ElectricityNetwork" name="Site LV Network" id="9ef78c55-38d8-446d-85ef-75a0fcc336a1">
        <port xsi:type="esdl:OutPort" name="net_to_datacenter" id="4a6ae9bb-a3eb-47e8-a4d3-84f636f3c9d9" connectedTo="9886a7b2-557d-495f-b22b-fc50bb417347"/>
        <port xsi:type="esdl:OutPort" name="net_to_bess" id="5c86db80-e9b0-457e-b65f-69857c329494" connectedTo="faeab5f6-0461-46e5-9e2a-c3b5e0f439ba"/>
        <port xsi:type="esdl:InPort" name="net_from_bess" id="48f83b70-1336-40f9-b671-aef9b181f246" connectedTo="d06055c6-306c-4007-8128-9dd14e294038"/>
        <port xsi:type="esdl:OutPort" name="net_to_grid" id="b96938f1-496b-4681-aedd-aadec946b9a2" connectedTo="01e2a5b5-4944-43b9-ba06-44c8379ba9ad"/>
        <port xsi:type="esdl:InPort" name="net_from_grid" id="1bd8afa9-7969-4df0-969d-7a4405a84f2e" connectedTo="3e022a6d-a935-4bfc-99bf-ed56fb95bcda"/>
        <port xsi:type="esdl:InPort" name="net_from_backup_generator" id="d5338307-af6b-4e00-8a13-519b114fd79f" connectedTo="de9d655d-cc5b-4238-8dd6-018d599dc4d6"/>
        <port xsi:type="esdl:InPort" name="net_from_local_res" id="137ee3fc-b041-4d37-ac1d-c26db29ed0a7" connectedTo="6f845c90-804d-4ccb-8b43-8adfde0e4619"/>
      </asset>
      <asset xsi:type="esdl:ElectricityDemand" name="Datacenter Load" powerFactor="0.95" power="4000000.0" id="fae8f2ab-3199-4b23-b456-a4c452eabb96">
        <port xsi:type="esdl:InPort" name="dc_in" id="9886a7b2-557d-495f-b22b-fc50bb417347" connectedTo="4a6ae9bb-a3eb-47e8-a4d3-84f636f3c9d9"/>
      </asset>
      <asset xsi:type="esdl:Battery" name="Datacenter BESS" capacity="40000000.0" maxDischargeRate="4000000.0" id="ebfbcc14-0b31-4a8e-a7d2-3219a563cdbe" maxChargeRate="4000000.0" dischargeEfficiency="0.95" chargeEfficiency="0.95">
        <port xsi:type="esdl:InPort" name="bess_in" id="faeab5f6-0461-46e5-9e2a-c3b5e0f439ba" connectedTo="5c86db80-e9b0-457e-b65f-69857c329494"/>
        <port xsi:type="esdl:OutPort" name="bess_out" id="d06055c6-306c-4007-8128-9dd14e294038" connectedTo="48f83b70-1336-40f9-b671-aef9b181f246"/>
      </asset>
      <asset xsi:type="esdl:PowerPlant" minLoad="-75000000" name="Grid Connection" power="75000000.0" id="7846574e-ebe5-4d68-ae86-e4cb816eb250" efficiency="1.0">
        <port xsi:type="esdl:InPort" name="grid_in" id="01e2a5b5-4944-43b9-ba06-44c8379ba9ad" connectedTo="b96938f1-496b-4681-aedd-aadec946b9a2"/>
        <port xsi:type="esdl:OutPort" name="grid_out" id="3e022a6d-a935-4bfc-99bf-ed56fb95bcda" connectedTo="1bd8afa9-7969-4df0-969d-7a4405a84f2e"/>
      </asset>
      <asset xsi:type="esdl:GasProducer" name="Backup Generator" power="5000000.0" id="a7095133-0f01-48bc-9927-bcd7376e9702">
        <port xsi:type="esdl:OutPort" name="gen_out" id="de9d655d-cc5b-4238-8dd6-018d599dc4d6" connectedTo="d5338307-af6b-4e00-8a13-519b114fd79f"/>
        <KPIs xsi:type="esdl:KPIs" id="60d36bdb-704f-43bd-b86d-d8365ecab1a3">
          <kpi xsi:type="esdl:DoubleKPI" id="6b908342-20d2-4b39-a05d-fdebac3827bc" value="60.0" name="startup_delay_s"/>
        </KPIs>
      </asset>
      <asset xsi:type="esdl:PVInstallation" surfaceArea="5000" name="Local RES" angle="35" power="1000000.0" panelEfficiency="0.2" id="b457b55f-2407-4a90-9f1d-30ac1e8bd4d4" orientation="180" inverterEfficiency="0.98">
        <port xsi:type="esdl:OutPort" name="res_out" id="6f845c90-804d-4ccb-8b43-8adfde0e4619" connectedTo="137ee3fc-b041-4d37-ac1d-c26db29ed0a7"/>
      </asset>
    </area>
  </instance>
</esdl:EnergySystem>
