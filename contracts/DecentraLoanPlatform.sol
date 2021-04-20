// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./DecentraLoan.sol";

contract DecentraLoanPlatform {
    address[] private _loans;
    
    address private _owner;
    bool private _obsolete;

    constructor () {
        _owner = msg.sender;
        _obsolete = false;
    }

    function GetLoans() public view returns (address[] memory) {
        require(!_obsolete);
        
        return _loans;
    }

    // Loan Factory Methods
    function NewLoan(
        address lender,
        uint256 amount,
        uint256 interest,
        uint256 months,
        uint256 platform
    ) 
    public 
    payable 
    {
        require(!_obsolete);
        
        DecentraLoan newContract = new DecentraLoan(lender, amount, interest, months, platform);
        
        address contractAddress = address(newContract);
       
        _loans.push(contractAddress);
    }
    
    function Decomise() public payable {
        require(!_obsolete);
        require(msg.sender == _owner);
        _obsolete = true;
    }

}