module ansi_module_a (
  input var logic a,
  input var logic b
);

  logic c;
  wire d;

  ansi_module_b ansi_module_b_i (
    .e(d)
  );
  
endmodule