#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/csma-module.h"
#include "ns3/internet-module.h"
#include "ns3/ipv4-global-routing-helper.h"
#include "ns3/netanim-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/flow-monitor-module.h"

// Default Network Topology

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("CN_Assignment4_CustomTopology");

Ipv4InterfaceContainer CreateLink(Ptr<Node> node1, Ptr<Node> node2, const std::string &capacity, const std::string &delay, const std::string &baseAddr, double dropRate = 0.0)
{ // Default drop rate is 0%

    PointToPointHelper p2p;
    p2p.SetDeviceAttribute("DataRate", StringValue(capacity));
    p2p.SetChannelAttribute("Delay", StringValue(delay));
    NetDeviceContainer devices = p2p.Install(node1, node2);

    if (dropRate > 0.0)
    {
        // Configure the error model for packet drops
        Ptr<RateErrorModel> errorModel = CreateObject<RateErrorModel>();
        errorModel->SetAttribute("ErrorRate", DoubleValue(dropRate));

        // Attach the error model to both devices in the link
        devices.Get(1)->SetAttribute("ReceiveErrorModel", PointerValue(errorModel));
    }

    Ipv4AddressHelper ipv4;
    ipv4.SetBase(baseAddr.c_str(), "255.255.255.0"); // Make sure baseAddr is a valid string
    Ipv4InterfaceContainer interfaces = ipv4.Assign(devices);

    return interfaces;
}

int main(int argc, char *argv[])
{
    // Set up logging
    LogComponentEnable("UdpEchoClientApplication", LOG_LEVEL_INFO);
    LogComponentEnable("UdpEchoServerApplication", LOG_LEVEL_INFO);

    // Set up the simulation parameters
    uint32_t packet_size = 256;  // 256 bytes  = 2048 bits
    double Simulation_time = 60; // seconds
    const std::string propagation_delay = "1ms";
    const double packet_drop_rate = 0.000; // 5% packet drop rate
    // Traffic matrix representing average number of packets sent between nodes
    // int trafficMatrix[7][7] = {
    //     {0, 13, 17, 17, 9, 13, 13}, // A -> A, B, C, D, ..., G
    //     {13, 0, 18, 5, 6, 9, 7},    // B -> ...
    //     {9, 11, 0, 14, 16, 11, 10}, // C -> ...
    //     {12, 7, 7, 0, 3, 13, 6},    // D -> ...
    //     {9, 11, 12, 8, 0, 7, 7},    // E -> ...
    //     {14, 7, 11, 10, 9, 0, 13},  // F -> ...
    //     {9, 8, 14, 11, 8, 10, 0}    // G -> ...
    // };

    int trafficMatrix[7][7] = {
        {0, 0, 0, 0, 1, 1, 1}, // A -> E, F, G
        {0, 0, 0, 0, 1, 1, 1}, // B -> E, F, G
        {0, 0, 0, 0, 1, 1, 1}, // C -> E, F, G
        {0, 0, 0, 0, 1, 1, 1}, // D -> E, F, G
        {0, 0, 0, 0, 0, 0, 0}, // E
        {0, 0, 0, 0, 0, 0, 0}, // F
        {0, 0, 0, 0, 0, 0, 0}  // G
    };

    // Create nodes
    NodeContainer routers;
    routers.Create(4); // R1, R2, R3, R4

    NodeContainer workstations;
    workstations.Create(7); // A, B, C, D, E, F, G

    // Install internet stack on all nodes
    InternetStackHelper internet;
    internet.Install(routers);
    internet.Install(workstations);

    // Connect workstations and routers with point-to-point links
    Ipv4InterfaceContainer workstationInterfaces[7];

    // Create and force propagation delay for router connections
    CreateLink(routers.Get(0), routers.Get(1), "3Mbps", propagation_delay, "10.1.1.0", packet_drop_rate);   // R1 - R2 (1% drop rate)
    CreateLink(routers.Get(1), routers.Get(2), "2.5Mbps", propagation_delay, "10.1.2.0", packet_drop_rate); // R2 - R3 (1% drop rate)
    CreateLink(routers.Get(2), routers.Get(3), "1.5Mbps", propagation_delay, "10.1.3.0", packet_drop_rate); // R3 - R4 (1% drop rate)
    CreateLink(routers.Get(3), routers.Get(0), "1Mbps", propagation_delay, "10.1.4.0", packet_drop_rate);   // R4 - R1 (1% drop rate)

    // Connect workstations to routers
    workstationInterfaces[0] = CreateLink(routers.Get(0), workstations.Get(0), "1Mbps", propagation_delay, "10.1.5.0", packet_drop_rate);  // R1 - A
    workstationInterfaces[1] = CreateLink(routers.Get(0), workstations.Get(1), "1Mbps", propagation_delay, "10.1.6.0", packet_drop_rate);  // R1 - B
    workstationInterfaces[2] = CreateLink(routers.Get(1), workstations.Get(2), "1Mbps", propagation_delay, "10.1.7.0", packet_drop_rate);  // R2 - C
    workstationInterfaces[3] = CreateLink(routers.Get(1), workstations.Get(3), "2Mbps", propagation_delay, "10.1.8.0", packet_drop_rate);  // R2 - D
    workstationInterfaces[4] = CreateLink(routers.Get(2), workstations.Get(4), "1Mbps", propagation_delay, "10.1.9.0", packet_drop_rate);  // R3 - E
    workstationInterfaces[5] = CreateLink(routers.Get(2), workstations.Get(5), "1Mbps", propagation_delay, "10.1.10.0", packet_drop_rate); // R3 - F
    workstationInterfaces[6] = CreateLink(routers.Get(3), workstations.Get(6), "1Mbps", propagation_delay, "10.1.11.0", packet_drop_rate); // R4 - G

    // Setup UDP echo applications (simulating traffic between workstations)
    uint16_t port = 9;
    ApplicationContainer clientApps;
    ApplicationContainer serverApps;

    // Iterate over all traffic matrix and set up the client-server applications
    for (uint32_t i = 0; i < workstations.GetN(); ++i)
    {
        for (uint32_t j = 0; j < workstations.GetN(); ++j)
        {
            if (trafficMatrix[i][j] > 0)
            {
                port++;
                // Client sends traffic to Server
                Ipv4Address serverAddress = workstationInterfaces[j].GetAddress(1); // Get the IP address of workstation j
                UdpEchoClientHelper client(serverAddress, port);
                client.SetAttribute("MaxPackets", UintegerValue(trafficMatrix[i][j]));
                client.SetAttribute("Interval", TimeValue(Seconds(1.0)));
                client.SetAttribute("PacketSize", UintegerValue(packet_size));
                clientApps.Add(client.Install(workstations.Get(i)));

                // Server listens for traffic
                UdpEchoServerHelper server(port);
                serverApps.Add(server.Install(workstations.Get(j)));
            }
        }
    }

    // Start applications
    serverApps.Start(Seconds(1.0));
    clientApps.Start(Seconds(2.0));

    // Populate routing tables
    Ipv4GlobalRoutingHelper::PopulateRoutingTables();

    // Create the NetAnim file for visualization
    AnimationInterface anim("custom_topology.xml"); // Create the NetAnim file

    // Set the sizes of the routers (bigger size)
    anim.UpdateNodeSize(routers.Get(0), 5, 5); // R1
    anim.UpdateNodeSize(routers.Get(1), 5, 5); // R2
    anim.UpdateNodeSize(routers.Get(2), 5, 5); // R3
    anim.UpdateNodeSize(routers.Get(3), 5, 5); // R4

    // Set the positions of the routers (centered in the network)
    anim.SetConstantPosition(routers.Get(0), 50.0, 50.0);   // R1 at position
    anim.SetConstantPosition(routers.Get(1), 150.0, 50.0);  // R2 at position
    anim.SetConstantPosition(routers.Get(2), 150.0, 150.0); // R3 at position
    anim.SetConstantPosition(routers.Get(3), 50.0, 150.0);  // R4 at position

    // Workstation positions (set around the routers with smaller sizes)
    anim.UpdateNodeSize(workstations.Get(0), 2, 2); // A
    anim.UpdateNodeSize(workstations.Get(1), 2, 2); // B
    anim.UpdateNodeSize(workstations.Get(2), 2, 2); // C
    anim.UpdateNodeSize(workstations.Get(3), 2, 2); // D
    anim.UpdateNodeSize(workstations.Get(4), 2, 2); // E
    anim.UpdateNodeSize(workstations.Get(5), 2, 2); // F
    anim.UpdateNodeSize(workstations.Get(6), 2, 2); // G

    // Set the positions of the workstations (around routers)
    anim.SetConstantPosition(workstations.Get(0), 30.0, 30.0);   // A near R1
    anim.SetConstantPosition(workstations.Get(1), 30.0, 70.0);   // B near R1
    anim.SetConstantPosition(workstations.Get(2), 170.0, 30.0);  // C near R2
    anim.SetConstantPosition(workstations.Get(3), 170.0, 70.0);  // D near R2
    anim.SetConstantPosition(workstations.Get(4), 170.0, 130.0); // E near R3
    anim.SetConstantPosition(workstations.Get(5), 170.0, 170.0); // F near R3
    anim.SetConstantPosition(workstations.Get(6), 30.0, 130.0);  // G near R4

    // Flow Monitor
    FlowMonitorHelper flowmonHelper;
    Ptr<FlowMonitor> monitor = flowmonHelper.InstallAll();

    // Run the simulation after setting up positions
    Simulator::Stop(Seconds(Simulation_time));
    Simulator::Run();

    // Print FlowMonitor statistics
    monitor->CheckForLostPackets();
    Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier>(flowmonHelper.GetClassifier());
    FlowMonitor::FlowStatsContainer stats = monitor->GetFlowStats();

    for (auto iter = stats.begin(); iter != stats.end(); ++iter)
    {
        Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow(iter->first);
        NS_LOG_UNCOND("Flow " << iter->first << " (" << t.sourceAddress << " -> " << t.destinationAddress << ")");
        NS_LOG_UNCOND("Tx Packets: " << iter->second.txPackets);
        NS_LOG_UNCOND("Rx Packets: " << iter->second.rxPackets);
        NS_LOG_UNCOND("Lost Packets: " << iter->second.txPackets - iter->second.rxPackets);

        // Throughput Calculation
        double throughput = (iter->second.rxBytes * 8.0) / (iter->second.timeLastRxPacket.GetSeconds() - iter->second.timeFirstTxPacket.GetSeconds()) / 1000; // Throughput in kbps
        NS_LOG_UNCOND("Throughput: " << throughput << " kbps");

        // Delay Calculation
        double avgDelay = (iter->second.rxPackets > 0) ? (iter->second.delaySum.GetSeconds() / iter->second.rxPackets) : 0.0; // Average delay in seconds
        NS_LOG_UNCOND("Average Delay: " << avgDelay << " seconds");

        // Jitter Calculation
        double avgJitter = (iter->second.rxPackets > 1) ? (iter->second.jitterSum.GetSeconds() / (iter->second.rxPackets - 1)) : 0.0; // Average jitter in seconds
        NS_LOG_UNCOND("Average Jitter: " << avgJitter << " seconds");
    }

    Simulator::Destroy();
}
