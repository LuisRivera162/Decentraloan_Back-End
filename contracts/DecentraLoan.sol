// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DecentraLoan {
    enum StateType {
        Available,
        DealReached,
        Active,
        AwaitingValidation,
        Delinquent,
        Terminated,
        Withdrawn
    }

    enum EvidenceStatus {
        Unverified, 
        Invalid, 
        Valid
    }

    struct Evidence {
        address sender;
        string transactionHash;
        EvidenceStatus evidenceStatus;
    }

    // contract owner (who pays for the gas fees..)
    address private _owner;
    address payable[10] private _investors;
    uint256 InvestorIndex;

    // lender specific variables
    address private Lender;
    address private Borrower;
    uint256 private LoanAmount;
    uint256 private InterestRate;
    uint256 private RepaymentPeriod;
    uint256 private Platform;

    // loan contract specific variables
    StateType private State;
    Evidence[] private Evidences;
    uint256 private Balance;
    uint256 private PaymentNumber;

    // contract constructor
    constructor(
        address owner,
        address lender,
        uint256 amount,
        uint256 interest,
        uint256 repaymentPeriod,
        uint256 platform
    ) {
        Lender = lender;
        LoanAmount = amount;
        InterestRate = interest;
        RepaymentPeriod = repaymentPeriod;
        Platform = platform;

        _owner = owner;

        State = StateType.Available;

        PaymentNumber = 0;

        emit Created(lender, amount, interest, repaymentPeriod);
    }
    
    function GetLoanAmount() public view returns (uint256) {
        return LoanAmount;
    }
    
    function Invest() public payable {
        require(InvestorIndex < 10);
        require(msg.value == ((LoanAmount/10)*(5e14)));
        
        _investors[InvestorIndex] = payable(msg.sender);
        InvestorIndex++;
    }
    
    function GetInvestors() public view returns (address payable[10] memory) {
        return _investors;
    }
    
    function PayInvestors() public payable {
        for (uint256 i = 0; i < InvestorIndex; i++) {
            _investors[i].transfer((LoanAmount/10)*(5e14));
        }
    }

    // modify available (non-active) contract [lender]
    function Modify(
        // address user,
        uint256 amount,
        uint256 interest,
        uint256 repaymentPeriod
    ) public payable {
        require(msg.sender == _owner);
        // require(user == Lender);
        require(State == StateType.Available);

        LoanAmount = amount;
        InterestRate = interest;
        RepaymentPeriod = repaymentPeriod;

        emit Modified(Lender, amount, interest, repaymentPeriod);
    }

    // leander and borrower reached a deal, 
    // do virtual handshake and set loan state to Active
    function Deal(
        // address user,
        address _borrower,
        uint256 _amount,
        uint256 _interest,
        uint256 _repaymentPeriod
    ) public payable {
        require(msg.sender == _owner);
        // require(user == Lender);
        require(State == StateType.Available);

        // set borrower
        Borrower = _borrower;
        
        // change loan parameters if reached deal changed any
        LoanAmount = _amount;
        InterestRate = _interest;
        RepaymentPeriod = _repaymentPeriod;

        // set loan status to Active
        State = StateType.Active;

        emit DealReached(
            Lender,
            Borrower,
            LoanAmount,
            InterestRate,
            RepaymentPeriod
        );
    }

    function Withdraw() public payable {
        require(msg.sender == _owner);
        require(State == StateType.Available);
        // require(_lender == Lender);

        State = StateType.Withdrawn;

        emit Withdrawn(Lender);
    }

    // sends payment with required evidence attached [lender|borrower]
    function SendPayment(
        address sender,
        uint256 paymentNumber,
        uint256 amount,
        string memory evidence
    ) public payable {
        require(msg.sender == _owner);
        require(sender == Lender || sender == Borrower || sender == _owner); // require sender is lender or borrower
        require(State == StateType.Active); // require that it is an active contract
        require(amount > 0); // require payment amount is not 0

        if (PaymentNumber == 0) {
            // Lender sent core loan amount, this is considered as payment 0.
            Balance = amount;
        } else {
            // subtract paid amount to the balance
            Balance = Balance - amount;
        }

        // send evidence for counterparty validation, initialy unverified
        Evidences.push(
            Evidence(
                sender,
                evidence,
                EvidenceStatus.Unverified
            )
        );

        State = StateType.AwaitingValidation; // set state to awaiting validation

        emit PaymentSent(
            sender,
            amount,
            paymentNumber,
            Evidences[paymentNumber].transactionHash
        );
    }

    function GetEvidence(uint256 paymentNumber)
        public
        view
        returns (Evidence memory)
    {
        require(paymentNumber <= PaymentNumber);

        return Evidences[paymentNumber];
    }

    function ValidateEvidence(address user)
        public
        payable
    {
        require(msg.sender == _owner);
        require(
            (user == Borrower && Evidences[PaymentNumber].sender == Lender) ||
                (user == Lender && Evidences[PaymentNumber].sender == Borrower)
        );
        require(State == StateType.AwaitingValidation);

        // validate from website, validation code is stored encrypted in the blockchain
        // encryption is only lifted by having the decryption key that is server unique
        // after some checks, validate...
        Evidences[PaymentNumber].evidenceStatus = EvidenceStatus.Valid;

        State = StateType.Active; // set loan state back to active

        emit PaymentValidated(
            user,
            PaymentNumber,
            Evidences[PaymentNumber].transactionHash
        );
        
        PaymentNumber++;
    }

    /**
     * EVENTS
     **/
    event Received(address sender, uint256 amount);

    event Created(
        address lender,
        uint256 amount,
        uint256 interest,
        uint256 repaymentPeriod
    );
    event Modified(
        address lender,
        uint256 amount,
        uint256 interest,
        uint256 repaymentPeriod
    );
    event Withdrawn(
        address lender
    );
    event DealReached(
        address lender,
        address borrower,
        uint256 amount,
        uint256 interest,
        uint256 repaymentPeriod
    );
    event PaymentSent(
        address sender,
        uint256 amount,
        uint256 paymentNumber,
        string evidence
    );
    event PaymentValidated(
        address sender,
        uint256 paymentNumber,
        string evidence
    );

    // Receive any ethereum randomly sent to the contract from outside
    receive() external payable {
        emit Received(msg.sender, msg.value);
    }

    // get tupple with information about current contract
    function Info()
        public
        view
        returns (
            address,
            address,
            uint256,
            uint256,
            uint256,
            uint256,
            uint256,
            StateType
        )
    {
        return (
            Lender,
            Borrower,
            LoanAmount,
            Balance,
            InterestRate,
            RepaymentPeriod,
            PaymentNumber,
            State
        );
    }
}