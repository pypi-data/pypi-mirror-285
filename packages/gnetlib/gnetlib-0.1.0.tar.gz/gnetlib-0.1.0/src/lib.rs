use pnet::packet::icmp::echo_request::MutableEchoRequestPacket;
use pnet::packet::icmp::IcmpTypes;
use pnet::packet::ip::IpNextHeaderProtocols;
use pnet::packet::Packet;
use pnet::transport::TransportChannelType::Layer4;
use pnet::transport::{icmp_packet_iter, transport_channel};
use std::net::{IpAddr, Ipv4Addr};
use std::time::Duration;
use pyo3::prelude::*;


#[pyfunction]
fn ping(ip: String) -> bool {
    let ip: Ipv4Addr = ip.parse().unwrap();
    let protocol = Layer4(pnet::transport::TransportProtocol::Ipv4(
        IpNextHeaderProtocols::Icmp,
    ));
    let (mut tx, mut rx) =
        transport_channel(1024, protocol).expect("Error creating transport channel");

    // building ping packet
    let mut packet = [0u8; 16];
    let mut icmp_packet =
        MutableEchoRequestPacket::new(&mut packet).expect("Error creating echo packet");
    icmp_packet.set_icmp_type(IcmpTypes::EchoRequest);
    icmp_packet.set_sequence_number(1);
    icmp_packet.set_identifier(1);

    let checksum = pnet::util::checksum(icmp_packet.packet(), 1);
    icmp_packet.set_checksum(checksum);

    // try to ping 5 times before giving up
    for _ in 0..5 {
        tx.send_to(&icmp_packet, IpAddr::V4(ip))
            .expect("Error sending packet");

        let mut iter = icmp_packet_iter(&mut rx);
        match iter.next_with_timeout(Duration::from_millis(100)) {
            Ok(Some((_packet, addr))) => {
                if addr == std::net::IpAddr::V4(ip) {
                    return true;
                }
            }
            Ok(None) => {}
            Err(e) => {
                panic!("error: {}", e);
            }
        }
    }
    false
}

// fn pings(ip: Vec<String>) -> Vec<bool> {}



/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn gnetlib(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(ping, m)?)?;
    Ok(())
}
