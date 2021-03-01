// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./DecentraLoan.sol";

contract DecentraLoanFactory {
    mapping(address => address[]) loans;

    function GetLoans(address user) public view returns (address[] memory) {
        return loans[user];
    }

    function CreateLoan(address lender, uint256 amount, uint256 interest, uint256 repayment_period)
        public
        payable
        returns (address loanAddress)
    {
        DecentraLoan loan = new DecentraLoan(msg.sender, lender, amount, interest, repayment_period);
        loanAddress = address(loan);

        loans[lender].push(loanAddress);

        // Emit Created() event.
        Created(loanAddress, msg.sender, lender, block.timestamp, amount, interest, repayment_period);
    }

    /**
     * Events
     */
    event Received(address, uint);
    event Created(address loan, address from, address to, uint256 createdAt, uint256 amount, uint256 interest, uint256 repayment_period);

    // Receive any ethereum randomly sent to the contract from outside
    receive() external payable {
        emit Received(msg.sender, msg.value);
    }
}
