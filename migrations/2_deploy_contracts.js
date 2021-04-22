var DecentraLoanPlatform = artifacts.require("DecentraLoanPlatform");
var DecentraLoanToken = artifacts.require("DecentraLoanToken");

module.exports = function(deployer) {
  deployer.deploy(DecentraLoanPlatform);
  deployer.deploy(DecentraLoanToken, "Decentraloan Token", "DLOAN", 100000000);
};