`timescale 1ns / 1ps
module tb;
	parameter integer C_S00_AXI_DATA_WIDTH	= 32;
	parameter integer C_S00_AXI_ADDR_WIDTH	= 4;
	parameter integer C_AXIS_DWIDTH = 512;


	reg s00_axi_aclk, axis_aclk;
	reg s00_axi_aresetn, axis_aresetn;
	
	reg s_axis_tvalid, m_axis_tready;
	reg [C_AXIS_DWIDTH-1:0] s_axis_tdata;
	wire [C_AXIS_DWIDTH-1:0] m_axis_tdata;
	
	wire s_axis_tready, m_axis_tvalid;
	wire m_axis_tlast;
	reg adc_control;
	
	initial begin
		s00_axi_aclk = 1'b0;
		s00_axi_aresetn = 1'b0;
		axis_aclk = 1'b0;
		axis_aresetn = 1'b0;
		
		s_axis_tvalid = 1'b0;
		m_axis_tready = 1'b0;
		s_axis_tdata = {C_AXIS_DWIDTH{1'b0}};
		adc_control = 1'b1;
		#50;
		axis_aresetn = 1'b1;
		s00_axi_aresetn = 1'b1;
		m_axis_tready = 1'b1;
//		#10000;
//		$finish;
	end
	
	always @ (*) begin
		s00_axi_aclk <= #10 ~s00_axi_aclk;
		axis_aclk <= #5 ~axis_aclk;
	end
	
	always @ (posedge axis_aclk or negedge axis_aresetn) begin
		if (~axis_aresetn) begin
			s_axis_tdata <= {C_AXIS_DWIDTH{1'b0}};
			s_axis_tvalid <= 1'b0;
		end
		else begin
			s_axis_tdata <= s_axis_tdata + 1'b1;
			s_axis_tvalid <= 1'b1;			
		end
	end
	
	axis_flow_ctrl_v1_0 #(
		.C_S00_AXI_DATA_WIDTH(C_S00_AXI_DATA_WIDTH),
		.C_S00_AXI_ADDR_WIDTH(C_S00_AXI_ADDR_WIDTH),
		.C_AXIS_DWIDTH(C_AXIS_DWIDTH)
	) dut (
		.s00_axi_aclk(s00_axi_aclk),
		.s00_axi_aresetn(s00_axi_aresetn),
		
		.s00_axi_awaddr({C_S00_AXI_ADDR_WIDTH{1'b0}}),
		.s00_axi_awprot(3'b0),
		.s00_axi_awvalid(1'b0),
		.s00_axi_wdata({C_S00_AXI_DATA_WIDTH{1'b0}}),
		.s00_axi_wstrb({(C_S00_AXI_DATA_WIDTH/8){1'b0}}),
		.s00_axi_wvalid(1'b0),
		.s00_axi_bready(1'b0),
		.s00_axi_araddr({C_S00_AXI_ADDR_WIDTH{1'b0}}),
		.s00_axi_arprot(3'b0),
		.s00_axi_arvalid(1'b0),
		.s00_axi_rready(1'b0),
		
		.axis_aclk(axis_aclk),
		.axis_aresetn(axis_aresetn),
		
		.s_axis_tvalid(s_axis_tvalid),
		.s_axis_tdata(s_axis_tdata),
		.s_axis_tready(s_axis_tready),
		
		.m_axis_tvalid(m_axis_tvalid),
		.m_axis_tdata(m_axis_tdata),
		.m_axis_tready(m_axis_tready),
		.m_axis_tlast(m_axis_tlast),
		
		.tlast(tlast)
	);
endmodule
