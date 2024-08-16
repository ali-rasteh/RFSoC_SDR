
`timescale 1 ns / 1 ps

module axis_flow_ctrl_v1_0 #
(
	parameter integer C_S00_AXI_DATA_WIDTH	= 32,
	parameter integer C_S00_AXI_ADDR_WIDTH	= 4,
	parameter integer C_AXIS_DWIDTH = 128
)(
	input wire  s00_axi_aclk,
	input wire  s00_axi_aresetn,
	input wire [C_S00_AXI_ADDR_WIDTH-1 : 0] s00_axi_awaddr,
	input wire [2 : 0] s00_axi_awprot,
	input wire  s00_axi_awvalid,
	output wire  s00_axi_awready,
	input wire [C_S00_AXI_DATA_WIDTH-1 : 0] s00_axi_wdata,
	input wire [(C_S00_AXI_DATA_WIDTH/8)-1 : 0] s00_axi_wstrb,
	input wire  s00_axi_wvalid,
	output wire  s00_axi_wready,
	output wire [1 : 0] s00_axi_bresp,
	output wire  s00_axi_bvalid,
	input wire  s00_axi_bready,
	input wire [C_S00_AXI_ADDR_WIDTH-1 : 0] s00_axi_araddr,
	input wire [2 : 0] s00_axi_arprot,
	input wire  s00_axi_arvalid,
	output wire  s00_axi_arready,
	output wire [C_S00_AXI_DATA_WIDTH-1 : 0] s00_axi_rdata,
	output wire [1 : 0] s00_axi_rresp,
	output wire  s00_axi_rvalid,
	input wire  s00_axi_rready,
	
	input axis_aclk,
	input axis_aresetn,
	
	// AXI-S Slave
	input s_axis_tvalid,
	input [C_AXIS_DWIDTH-1:0] s_axis_tdata,
	output s_axis_tready,
	
	// AXI-S Master
	output m_axis_tvalid,
	output [C_AXIS_DWIDTH-1:0] m_axis_tdata,
	input m_axis_tready,
	output m_axis_tlast,
	
	// AXI ADC Control
	input adc_control
);
	wire [C_S00_AXI_DATA_WIDTH-1:0] tdata_read_src;
	wire [C_S00_AXI_DATA_WIDTH-1:0] tdata_skip_src;
	wire [C_S00_AXI_DATA_WIDTH-1:0] tdata_nbytes_src;

	wire [C_S00_AXI_DATA_WIDTH-1:0] tdata_read;
	wire [C_S00_AXI_DATA_WIDTH-1:0] tdata_skip;
	wire [C_S00_AXI_DATA_WIDTH-1:0] tdata_nbytes;
	
	axis_flow_ctrl_v1_0_S00_AXI # ( 
		.C_S_AXI_DATA_WIDTH(C_S00_AXI_DATA_WIDTH),
		.C_S_AXI_ADDR_WIDTH(C_S00_AXI_ADDR_WIDTH)
	) axis_flow_ctrl_v1_0_S00_AXI_inst (
		.S_AXI_ACLK(s00_axi_aclk),
		.S_AXI_ARESETN(s00_axi_aresetn),
		.S_AXI_AWADDR(s00_axi_awaddr),
		.S_AXI_AWPROT(s00_axi_awprot),
		.S_AXI_AWVALID(s00_axi_awvalid),
		.S_AXI_AWREADY(s00_axi_awready),
		.S_AXI_WDATA(s00_axi_wdata),
		.S_AXI_WSTRB(s00_axi_wstrb),
		.S_AXI_WVALID(s00_axi_wvalid),
		.S_AXI_WREADY(s00_axi_wready),
		.S_AXI_BRESP(s00_axi_bresp),
		.S_AXI_BVALID(s00_axi_bvalid),
		.S_AXI_BREADY(s00_axi_bready),
		.S_AXI_ARADDR(s00_axi_araddr),
		.S_AXI_ARPROT(s00_axi_arprot),
		.S_AXI_ARVALID(s00_axi_arvalid),
		.S_AXI_ARREADY(s00_axi_arready),
		.S_AXI_RDATA(s00_axi_rdata),
		.S_AXI_RRESP(s00_axi_rresp),
		.S_AXI_RVALID(s00_axi_rvalid),
		.S_AXI_RREADY(s00_axi_rready),
		.tdata_read(tdata_read_src),
		.tdata_skip(tdata_skip_src),
		.tdata_nbytes(tdata_nbytes_src)
	);
	
    xpm_cdc_array_single #(
        .WIDTH(C_S00_AXI_DATA_WIDTH),
        .SRC_INPUT_REG(1'b0)
    )
    xpm_cdc_tdata_read (
        .dest_out(tdata_read),
        .dest_clk(axis_aclk),
        .src_clk(s00_axi_aclk),
        .src_in(tdata_read_src)
    );
    
    xpm_cdc_array_single #(
        .WIDTH(C_S00_AXI_DATA_WIDTH),
        .SRC_INPUT_REG(1'b0)
    )
    xpm_cdc_tdata_skip (
        .dest_out(tdata_skip),
        .dest_clk(axis_aclk),
        .src_clk(s00_axi_aclk),
        .src_in(tdata_skip_src)
    );
    
    xpm_cdc_array_single #(
        .WIDTH(C_S00_AXI_DATA_WIDTH),
        .SRC_INPUT_REG(1'b0)
    )
    xpm_cdc_tdata_nbytes (
        .dest_out(tdata_nbytes),
        .dest_clk(axis_aclk),
        .src_clk(s00_axi_aclk),
        .src_in(tdata_nbytes_src)
    );
	
	reg flag;
	reg [31:0] cntr;
	reg [31:0] byte_cntr;
//	assign s_axis_tready = adc_control && m_axis_tready;
	assign s_axis_tready = 1'b1;
	assign m_axis_tdata = s_axis_tdata;
//	assign m_axis_tvalid = adc_control && s_axis_tvalid && ((cntr < tdata_read) || (tdata_read == 32'h0000_0000));
	assign m_axis_tvalid = (~flag) && adc_control && axis_aresetn && ((cntr < tdata_read) || (tdata_read == 32'h0000_0000));
	
	always @ (posedge axis_aclk or negedge axis_aresetn) begin
		if (~axis_aresetn) begin
			cntr <= 32'h0000_0000;		
			byte_cntr <= 32'h0000_0000;
			flag <= 1'b0;	
		end
		else if (adc_control) begin
			if (m_axis_tlast || (cntr == (tdata_read + tdata_skip - 1'b1))) begin
				cntr <= 32'h0000_0000;		
			end
			else begin
				cntr <= cntr + 32'h0000_00001;
			end
			
			if (byte_cntr == tdata_nbytes) begin
				byte_cntr <= 32'h0000_0000;		
			end
			else if (m_axis_tvalid) begin
				byte_cntr <= byte_cntr + (C_AXIS_DWIDTH>>3);
			end
			
			flag <= flag || m_axis_tlast;
		end
	end
	
	assign m_axis_tlast = (byte_cntr == (tdata_nbytes - (C_AXIS_DWIDTH>>3)));
endmodule