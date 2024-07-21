# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Neudose(KaitaiStruct):
    """:field dest_callsign: ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_header.ctl
    :field pid: ax25_header.pid
    
    :field csp_hdr_crc: csp_header.crc
    :field csp_hdr_rdp: csp_header.rdp
    :field csp_hdr_xtea: csp_header.xtea
    :field csp_hdr_hmac: csp_header.hmac
    :field csp_hdr_src_port: csp_header.source_port
    :field csp_hdr_dst_port: csp_header.destination_port
    :field csp_hdr_destination: csp_header.destination
    :field csp_hdr_source: csp_header.source
    :field csp_hdr_priority: csp_header.priority
    
    :field last_rx_timestamp_raw: beacon.last_rx_timestamp_raw
    :field packet_version: beacon.packet_version
    :field unix_timestamp: beacon.unix_timestamp
    
    :field cdh_on: beacon.sat_status.cdh_on
    :field eps_on: beacon.sat_status.eps_on
    :field comms_on: beacon.sat_status.comms_on
    :field antenna_on: beacon.sat_status.antenna_on
    :field payload_on: beacon.sat_status.payload_on
    :field mech: beacon.sat_status.mech
    :field thermal: beacon.sat_status.thermal
    :field antenna_deployed: beacon.sat_status.antenna_deployed
    
    :field last_gs_conn_timestamp: beacon.last_gs_conn_timestamp
    
    :field eps_bat_state: beacon.eps_status.bat_state
    :field eps_bat_htr_state: beacon.eps_status.bat_htr_state
    :field eps_bat_htr_mode: beacon.eps_status.bat_htr_mode
    :field eps_last_reset_rsn: beacon.eps_status.last_reset_rsn
    :field eps_gs_wtdg_rst_mark: beacon.eps_status.gs_wtdg_rst_mark
    
    :field eps_uptime: beacon.eps_uptime
    :field eps_vbat: beacon.eps_vbat
    :field eps_bat_chrge_curr: beacon.eps_bat_chrge_curr
    :field eps_bat_dischrge_curr: beacon.eps_bat_dischrge_curr
    
    :field eps_mppt_conv1_temp: beacon.eps_temp.mppt_conv1
    :field eps_mppt_conv2_temp: beacon.eps_temp.mppt_conv2
    :field eps_mppt_conv3_temp: beacon.eps_temp.mppt_conv3
    :field eps_out_conv_3v3_temp: beacon.eps_temp.out_conv_3v3
    :field eps_out_conv_5v0_temp: beacon.eps_temp.out_conv_5v0
    :field eps_battery_pack_temp: beacon.eps_temp.battery_pack
    
    :field eps_solar_panel_y_n_curr: beacon.eps_solar_panel_curr.y_n
    :field eps_solar_panel_y_p_curr: beacon.eps_solar_panel_curr.y_p
    :field eps_solar_panel_x_n_curr: beacon.eps_solar_panel_curr.x_n
    :field eps_solar_panel_x_p_curr: beacon.eps_solar_panel_curr.x_p
    :field eps_solar_panel_z_n_curr: beacon.eps_solar_panel_curr.z_n
    :field eps_solar_panel_z_p_curr: beacon.eps_solar_panel_curr.z_p
    
    :field eps_cdh_channel_curr_out: beacon.eps_channel_curr_out.cdh
    :field eps_comm_3v3_channel_curr_out: beacon.eps_channel_curr_out.comm_3v3
    :field eps_comm_5v0_channel_curr_out: beacon.eps_channel_curr_out.comm_5v0
    :field eps_ant_channel_curr_out: beacon.eps_channel_curr_out.ant
    :field eps_pld_channel_curr_out: beacon.eps_channel_curr_out.pld
    
    :field cdh_curr_state: beacon.cdh_curr_state
    :field cdh_prev_state: beacon.cdh_prev_state
    
    :field cdh_reset_cause: beacon.cdh_boot_reset_cause.reset_cause
    :field cdh_boot_cause: beacon.cdh_boot_reset_cause.boot_cause
    
    :field cdh_uptime: beacon.cdh_uptime
    :field cdh_temp_mcu_raw: beacon.cdh_temp_mcu_raw
    :field cdh_temp_ram_raw: beacon.cdh_temp_ram_raw
    
    :field comms_rtsm_state: beacon.comms_status.rtsm_state
    :field comms_rst_reason: beacon.comms_status.rst_reason
    :field comms_boot_img_bank: beacon.comms_status.boot_img_bank
    
    :field comms_uptime_raw: beacon.comms_uptime_raw
    :field comms_ina233_pa_curr_raw: beacon.comms_ina233_pa_curr_raw
    :field comms_ad7294_pa_curr_raw: beacon.comms_ad7294_pa_curr_raw
    :field comms_ad7294_gate_volt_raw: beacon.comms_ad7294_gate_volt_raw
    :field comms_cc1125_rssi_raw: beacon.comms_cc1125_rssi_raw
    
    :field comms_lna_therm_temp: beacon.comms_temp.lna_therm
    :field comms_lna_diode_temp: beacon.comms_temp.lna_diode
    :field comms_stm32_internal_temp: beacon.comms_temp.stm32_internal
    :field comms_cc1125_uhf_temp: beacon.comms_temp.cc1125_uhf
    :field comms_cc1125_vhf_temp: beacon.comms_temp.cc1125_vhf
    :field comms_pa_therm_temp: beacon.comms_temp.pa_therm
    :field comms_pa_diode_temp: beacon.comms_temp.pa_diode
    :field comms_pa_therm_strap_temp: beacon.comms_temp.pa_therm_strap
    :field comms_ad7294_internal_temp: beacon.comms_temp.ad7294_internal
    
    :field ant_deployment_status: beacon.ant_deployment_status
    :field ant_prev_isis_status: beacon.ant_prev_isis_status
    :field pld_status: beacon.pld_status
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_header = Neudose.Ax25HeaderT(self._io, self, self._root)
        self.csp_header = Neudose.CspHeaderT(self._io, self, self._root)
        self.beacon = Neudose.BeaconT(self._io, self, self._root)

    class EpsSolarPanelCurrT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.eps_solar_panel_curr = self._io.read_bytes(12)

        @property
        def z_p(self):
            if hasattr(self, '_m_z_p'):
                return self._m_z_p if hasattr(self, '_m_z_p') else None

            self._m_z_p = ((KaitaiStream.byte_array_index(self.eps_solar_panel_curr, 10) << 8) + KaitaiStream.byte_array_index(self.eps_solar_panel_curr, 11))
            return self._m_z_p if hasattr(self, '_m_z_p') else None

        @property
        def x_p(self):
            if hasattr(self, '_m_x_p'):
                return self._m_x_p if hasattr(self, '_m_x_p') else None

            self._m_x_p = ((KaitaiStream.byte_array_index(self.eps_solar_panel_curr, 6) << 8) + KaitaiStream.byte_array_index(self.eps_solar_panel_curr, 7))
            return self._m_x_p if hasattr(self, '_m_x_p') else None

        @property
        def y_p(self):
            if hasattr(self, '_m_y_p'):
                return self._m_y_p if hasattr(self, '_m_y_p') else None

            self._m_y_p = ((KaitaiStream.byte_array_index(self.eps_solar_panel_curr, 2) << 8) + KaitaiStream.byte_array_index(self.eps_solar_panel_curr, 3))
            return self._m_y_p if hasattr(self, '_m_y_p') else None

        @property
        def x_n(self):
            if hasattr(self, '_m_x_n'):
                return self._m_x_n if hasattr(self, '_m_x_n') else None

            self._m_x_n = ((KaitaiStream.byte_array_index(self.eps_solar_panel_curr, 4) << 8) + KaitaiStream.byte_array_index(self.eps_solar_panel_curr, 5))
            return self._m_x_n if hasattr(self, '_m_x_n') else None

        @property
        def y_n(self):
            if hasattr(self, '_m_y_n'):
                return self._m_y_n if hasattr(self, '_m_y_n') else None

            self._m_y_n = ((KaitaiStream.byte_array_index(self.eps_solar_panel_curr, 0) << 8) + KaitaiStream.byte_array_index(self.eps_solar_panel_curr, 1))
            return self._m_y_n if hasattr(self, '_m_y_n') else None

        @property
        def z_n(self):
            if hasattr(self, '_m_z_n'):
                return self._m_z_n if hasattr(self, '_m_z_n') else None

            self._m_z_n = ((KaitaiStream.byte_array_index(self.eps_solar_panel_curr, 8) << 8) + KaitaiStream.byte_array_index(self.eps_solar_panel_curr, 9))
            return self._m_z_n if hasattr(self, '_m_z_n') else None


    class SatStatusT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sat_status = self._io.read_u1()

        @property
        def comms_on(self):
            if hasattr(self, '_m_comms_on'):
                return self._m_comms_on if hasattr(self, '_m_comms_on') else None

            self._m_comms_on = ((self.sat_status >> 5) & 1)
            return self._m_comms_on if hasattr(self, '_m_comms_on') else None

        @property
        def antenna_on(self):
            if hasattr(self, '_m_antenna_on'):
                return self._m_antenna_on if hasattr(self, '_m_antenna_on') else None

            self._m_antenna_on = ((self.sat_status >> 4) & 1)
            return self._m_antenna_on if hasattr(self, '_m_antenna_on') else None

        @property
        def cdh_on(self):
            if hasattr(self, '_m_cdh_on'):
                return self._m_cdh_on if hasattr(self, '_m_cdh_on') else None

            self._m_cdh_on = ((self.sat_status >> 7) & 1)
            return self._m_cdh_on if hasattr(self, '_m_cdh_on') else None

        @property
        def mech(self):
            if hasattr(self, '_m_mech'):
                return self._m_mech if hasattr(self, '_m_mech') else None

            self._m_mech = ((self.sat_status >> 2) & 1)
            return self._m_mech if hasattr(self, '_m_mech') else None

        @property
        def antenna_deployed(self):
            if hasattr(self, '_m_antenna_deployed'):
                return self._m_antenna_deployed if hasattr(self, '_m_antenna_deployed') else None

            self._m_antenna_deployed = ((self.sat_status >> 0) & 1)
            return self._m_antenna_deployed if hasattr(self, '_m_antenna_deployed') else None

        @property
        def thermal(self):
            if hasattr(self, '_m_thermal'):
                return self._m_thermal if hasattr(self, '_m_thermal') else None

            self._m_thermal = ((self.sat_status >> 1) & 1)
            return self._m_thermal if hasattr(self, '_m_thermal') else None

        @property
        def eps_on(self):
            if hasattr(self, '_m_eps_on'):
                return self._m_eps_on if hasattr(self, '_m_eps_on') else None

            self._m_eps_on = ((self.sat_status >> 6) & 1)
            return self._m_eps_on if hasattr(self, '_m_eps_on') else None

        @property
        def payload_on(self):
            if hasattr(self, '_m_payload_on'):
                return self._m_payload_on if hasattr(self, '_m_payload_on') else None

            self._m_payload_on = ((self.sat_status >> 3) & 1)
            return self._m_payload_on if hasattr(self, '_m_payload_on') else None


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class Ax25HeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Neudose.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Neudose.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Neudose.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Neudose.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()
            self.pid = self._io.read_u1()


    class CommsStatusT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.comms_status = self._io.read_u1()

        @property
        def rtsm_state(self):
            if hasattr(self, '_m_rtsm_state'):
                return self._m_rtsm_state if hasattr(self, '_m_rtsm_state') else None

            self._m_rtsm_state = ((self.comms_status >> 5) & 7)
            return self._m_rtsm_state if hasattr(self, '_m_rtsm_state') else None

        @property
        def rst_reason(self):
            if hasattr(self, '_m_rst_reason'):
                return self._m_rst_reason if hasattr(self, '_m_rst_reason') else None

            self._m_rst_reason = ((self.comms_status >> 2) & 7)
            return self._m_rst_reason if hasattr(self, '_m_rst_reason') else None

        @property
        def boot_img_bank(self):
            if hasattr(self, '_m_boot_img_bank'):
                return self._m_boot_img_bank if hasattr(self, '_m_boot_img_bank') else None

            self._m_boot_img_bank = ((self.comms_status >> 0) & 3)
            return self._m_boot_img_bank if hasattr(self, '_m_boot_img_bank') else None


    class EpsChannelCurrOutT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.eps_channel_curr_out = self._io.read_bytes(10)

        @property
        def cdh(self):
            if hasattr(self, '_m_cdh'):
                return self._m_cdh if hasattr(self, '_m_cdh') else None

            self._m_cdh = ((KaitaiStream.byte_array_index(self.eps_channel_curr_out, 0) << 8) + KaitaiStream.byte_array_index(self.eps_channel_curr_out, 1))
            return self._m_cdh if hasattr(self, '_m_cdh') else None

        @property
        def ant(self):
            if hasattr(self, '_m_ant'):
                return self._m_ant if hasattr(self, '_m_ant') else None

            self._m_ant = ((KaitaiStream.byte_array_index(self.eps_channel_curr_out, 6) << 8) + KaitaiStream.byte_array_index(self.eps_channel_curr_out, 7))
            return self._m_ant if hasattr(self, '_m_ant') else None

        @property
        def comm_3v3(self):
            if hasattr(self, '_m_comm_3v3'):
                return self._m_comm_3v3 if hasattr(self, '_m_comm_3v3') else None

            self._m_comm_3v3 = ((KaitaiStream.byte_array_index(self.eps_channel_curr_out, 2) << 8) + KaitaiStream.byte_array_index(self.eps_channel_curr_out, 3))
            return self._m_comm_3v3 if hasattr(self, '_m_comm_3v3') else None

        @property
        def comm_5v0(self):
            if hasattr(self, '_m_comm_5v0'):
                return self._m_comm_5v0 if hasattr(self, '_m_comm_5v0') else None

            self._m_comm_5v0 = ((KaitaiStream.byte_array_index(self.eps_channel_curr_out, 4) << 8) + KaitaiStream.byte_array_index(self.eps_channel_curr_out, 5))
            return self._m_comm_5v0 if hasattr(self, '_m_comm_5v0') else None

        @property
        def pld(self):
            if hasattr(self, '_m_pld'):
                return self._m_pld if hasattr(self, '_m_pld') else None

            self._m_pld = ((KaitaiStream.byte_array_index(self.eps_channel_curr_out, 8) << 8) + KaitaiStream.byte_array_index(self.eps_channel_curr_out, 9))
            return self._m_pld if hasattr(self, '_m_pld') else None


    class CommsTempT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.lna_therm = self._io.read_s1()
            self.lna_diode = self._io.read_s1()
            self.stm32_internal = self._io.read_s1()
            self.cc1125_uhf = self._io.read_s1()
            self.cc1125_vhf = self._io.read_s1()
            self.pa_therm = self._io.read_s1()
            self.pa_diode = self._io.read_s1()
            self.pa_therm_strap = self._io.read_s1()
            self.ad7294_internal = self._io.read_s1()


    class BeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.last_rx_timestamp_raw = self._io.read_u4be()
            self.packet_version = self._io.read_u1()
            self.unix_timestamp = self._io.read_u4be()
            self.sat_status = Neudose.SatStatusT(self._io, self, self._root)
            self.last_gs_conn_timestamp = self._io.read_u4be()
            self.eps_status = Neudose.EpsStatusT(self._io, self, self._root)
            self.eps_uptime = self._io.read_u4be()
            self.eps_vbat = self._io.read_u2be()
            self.eps_bat_chrge_curr = self._io.read_u2be()
            self.eps_bat_dischrge_curr = self._io.read_u2be()
            self.eps_temp = Neudose.EpsTempT(self._io, self, self._root)
            self.eps_solar_panel_curr = Neudose.EpsSolarPanelCurrT(self._io, self, self._root)
            self.eps_channel_curr_out = Neudose.EpsChannelCurrOutT(self._io, self, self._root)
            self.cdh_curr_state = self._io.read_u1()
            self.cdh_prev_state = self._io.read_u1()
            self.cdh_boot_reset_cause = Neudose.CdhBootResetCauseT(self._io, self, self._root)
            self.cdh_uptime = self._io.read_u4be()
            self.cdh_temp_mcu_raw = self._io.read_s2be()
            self.cdh_temp_ram_raw = self._io.read_s2be()
            self.comms_status = Neudose.CommsStatusT(self._io, self, self._root)
            self.comms_uptime_raw = self._io.read_u4be()
            self.comms_ina233_pa_curr_raw = self._io.read_u2be()
            self.comms_ad7294_pa_curr_raw = self._io.read_u2be()
            self.comms_ad7294_gate_volt_raw = self._io.read_u2be()
            self.comms_cc1125_rssi_raw = self._io.read_u2be()
            self.comms_temp = Neudose.CommsTempT(self._io, self, self._root)
            self.ant_deployment_status = self._io.read_u1()
            self.ant_prev_isis_status = self._io.read_u2be()
            self.pld_status = self._io.read_u1()


    class SsidMask(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ssid_mask = self._io.read_u1()

        @property
        def ssid(self):
            if hasattr(self, '_m_ssid'):
                return self._m_ssid if hasattr(self, '_m_ssid') else None

            self._m_ssid = ((self.ssid_mask & 15) >> 1)
            return self._m_ssid if hasattr(self, '_m_ssid') else None


    class EpsTempT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mppt_conv1 = self._io.read_s1()
            self.mppt_conv2 = self._io.read_s1()
            self.mppt_conv3 = self._io.read_s1()
            self.out_conv_3v3 = self._io.read_s1()
            self.out_conv_5v0 = self._io.read_s1()
            self.battery_pack = self._io.read_s1()


    class CspHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_length = self._io.read_u2be()
            self.csp_header_raw = self._io.read_u4be()

        @property
        def source(self):
            if hasattr(self, '_m_source'):
                return self._m_source if hasattr(self, '_m_source') else None

            self._m_source = ((self.csp_header_raw >> 25) & 31)
            return self._m_source if hasattr(self, '_m_source') else None

        @property
        def source_port(self):
            if hasattr(self, '_m_source_port'):
                return self._m_source_port if hasattr(self, '_m_source_port') else None

            self._m_source_port = ((self.csp_header_raw >> 8) & 63)
            return self._m_source_port if hasattr(self, '_m_source_port') else None

        @property
        def destination_port(self):
            if hasattr(self, '_m_destination_port'):
                return self._m_destination_port if hasattr(self, '_m_destination_port') else None

            self._m_destination_port = ((self.csp_header_raw >> 14) & 63)
            return self._m_destination_port if hasattr(self, '_m_destination_port') else None

        @property
        def rdp(self):
            if hasattr(self, '_m_rdp'):
                return self._m_rdp if hasattr(self, '_m_rdp') else None

            self._m_rdp = ((self.csp_header_raw & 2) >> 1)
            return self._m_rdp if hasattr(self, '_m_rdp') else None

        @property
        def destination(self):
            if hasattr(self, '_m_destination'):
                return self._m_destination if hasattr(self, '_m_destination') else None

            self._m_destination = ((self.csp_header_raw >> 20) & 31)
            return self._m_destination if hasattr(self, '_m_destination') else None

        @property
        def priority(self):
            if hasattr(self, '_m_priority'):
                return self._m_priority if hasattr(self, '_m_priority') else None

            self._m_priority = (self.csp_header_raw >> 30)
            return self._m_priority if hasattr(self, '_m_priority') else None

        @property
        def reserved(self):
            if hasattr(self, '_m_reserved'):
                return self._m_reserved if hasattr(self, '_m_reserved') else None

            self._m_reserved = ((self.csp_header_raw >> 4) & 15)
            return self._m_reserved if hasattr(self, '_m_reserved') else None

        @property
        def xtea(self):
            if hasattr(self, '_m_xtea'):
                return self._m_xtea if hasattr(self, '_m_xtea') else None

            self._m_xtea = ((self.csp_header_raw & 4) >> 2)
            return self._m_xtea if hasattr(self, '_m_xtea') else None

        @property
        def hmac(self):
            if hasattr(self, '_m_hmac'):
                return self._m_hmac if hasattr(self, '_m_hmac') else None

            self._m_hmac = ((self.csp_header_raw & 8) >> 3)
            return self._m_hmac if hasattr(self, '_m_hmac') else None

        @property
        def crc(self):
            if hasattr(self, '_m_crc'):
                return self._m_crc if hasattr(self, '_m_crc') else None

            self._m_crc = (self.csp_header_raw & 1)
            return self._m_crc if hasattr(self, '_m_crc') else None


    class CallsignRaw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_callsign_ror = self._io.read_bytes(6)
            self._raw_callsign_ror = KaitaiStream.process_rotate_left(self._raw__raw_callsign_ror, 8 - (1), 1)
            _io__raw_callsign_ror = KaitaiStream(BytesIO(self._raw_callsign_ror))
            self.callsign_ror = Neudose.Callsign(_io__raw_callsign_ror, self, self._root)


    class CdhBootResetCauseT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cdh_boot_reset_cause = self._io.read_u1()

        @property
        def boot_cause(self):
            if hasattr(self, '_m_boot_cause'):
                return self._m_boot_cause if hasattr(self, '_m_boot_cause') else None

            self._m_boot_cause = ((self.cdh_boot_reset_cause >> 4) & 15)
            return self._m_boot_cause if hasattr(self, '_m_boot_cause') else None

        @property
        def reset_cause(self):
            if hasattr(self, '_m_reset_cause'):
                return self._m_reset_cause if hasattr(self, '_m_reset_cause') else None

            self._m_reset_cause = ((self.cdh_boot_reset_cause >> 0) & 15)
            return self._m_reset_cause if hasattr(self, '_m_reset_cause') else None


    class EpsStatusT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.eps_status = self._io.read_u1()

        @property
        def gs_wtdg_rst_mark(self):
            if hasattr(self, '_m_gs_wtdg_rst_mark'):
                return self._m_gs_wtdg_rst_mark if hasattr(self, '_m_gs_wtdg_rst_mark') else None

            self._m_gs_wtdg_rst_mark = ((self.eps_status >> 0) & 1)
            return self._m_gs_wtdg_rst_mark if hasattr(self, '_m_gs_wtdg_rst_mark') else None

        @property
        def bat_htr_mode(self):
            if hasattr(self, '_m_bat_htr_mode'):
                return self._m_bat_htr_mode if hasattr(self, '_m_bat_htr_mode') else None

            self._m_bat_htr_mode = ((self.eps_status >> 4) & 1)
            return self._m_bat_htr_mode if hasattr(self, '_m_bat_htr_mode') else None

        @property
        def bat_htr_state(self):
            if hasattr(self, '_m_bat_htr_state'):
                return self._m_bat_htr_state if hasattr(self, '_m_bat_htr_state') else None

            self._m_bat_htr_state = ((self.eps_status >> 5) & 1)
            return self._m_bat_htr_state if hasattr(self, '_m_bat_htr_state') else None

        @property
        def bat_state(self):
            if hasattr(self, '_m_bat_state'):
                return self._m_bat_state if hasattr(self, '_m_bat_state') else None

            self._m_bat_state = ((self.eps_status >> 6) & 3)
            return self._m_bat_state if hasattr(self, '_m_bat_state') else None

        @property
        def last_reset_rsn(self):
            if hasattr(self, '_m_last_reset_rsn'):
                return self._m_last_reset_rsn if hasattr(self, '_m_last_reset_rsn') else None

            self._m_last_reset_rsn = ((self.eps_status >> 1) & 7)
            return self._m_last_reset_rsn if hasattr(self, '_m_last_reset_rsn') else None



