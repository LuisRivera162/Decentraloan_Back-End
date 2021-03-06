// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DecentraLoan {
    enum StateType {
        Available,
        OfferPlaced,
        LenderAccepted,
        Confirmed,
        Active,
        AwaitingValidation,
        Delinquent,
        Terminated
    }

    enum EvidenceStatus {Unverified, Invalid, Valid}

    struct Evidence {
        address sender;
        string transactionHash;
        EvidenceStatus evidenceStatus;
    }

    // contract owner (who pays for the gas fees..)
    address public _owner;

    // lender specific variables
    address public Lender;
    uint256 public LoanAmount;
    uint256 public InterestRate;
    uint256 public RepaymentPeriod;

    // borrower specific variables
    address public Borrower;
    uint256 public OfferAmout;
    uint256 public OfferInterestRate;
    uint256 public OfferRepaymentPeriod;

    // loan contract specific variables
    StateType public State;
    Evidence[] public Evidences;
    uint256 public Balance;
    uint256 public PaymentNumber;

    // contract constructor [factory]
    constructor(
        address owner,
        address lender,
        uint256 amount,
        uint256 interest,
        uint256 repaymentPeriod
    ) {
        Lender = lender;
        LoanAmount = amount;
        InterestRate = interest;
        RepaymentPeriod = repaymentPeriod;

        Evidences = new Evidence[](repaymentPeriod + 1);

        _owner = owner; // set owner to custom address

        State = StateType.Available;

        PaymentNumber = 0;
    }

    // make offer with different terms [lender|borrower]
    function MakeOffer(
        address user,
        uint256 offerAmount,
        uint256 offerInterestRate,
        uint256 offerRepaymentPeriod
    ) public {
        require(msg.sender == _owner);
        require(user == Lender || user == Borrower);
        require(
            offerAmount != 0 &&
                offerRepaymentPeriod != 0 &&
                offerInterestRate != 0
        );
        require(State == StateType.Available || State == StateType.OfferPlaced);

        if (user != Lender) {
            Borrower = user;
        }

        OfferAmout = offerAmount;
        OfferInterestRate = offerInterestRate;
        OfferRepaymentPeriod = offerRepaymentPeriod;

        State = StateType.OfferPlaced;

        emit OfferPlaced(
            user,
            offerAmount,
            offerInterestRate,
            offerRepaymentPeriod
        );
    }

    // confirm lender offer [borrower]
    function ConfirmLenderOffer(address user) public {
        require(msg.sender == _owner);
        require(user == Borrower);
        require(State == StateType.LenderAccepted);

        // set state to confirmed (not active yet)
        State = StateType.Confirmed;

        emit BorrowerConfirmed(Borrower);
    }

    // modify available (non-active) contract [lender]
    function Modify(
        address user,
        uint256 amount,
        uint256 interest,
        uint256 repaymentPeriod
    ) public {
        require(msg.sender == _owner);
        require(user == Lender);
        require(State == StateType.Available);

        LoanAmount = amount;
        InterestRate = interest;
        RepaymentPeriod = repaymentPeriod;

        emit ContractModified(Lender, amount, interest, repaymentPeriod);
    }

    // accept borrower offer [lender]
    function AcceptOffer(address user) public {
        require(msg.sender == _owner);
        require(user == Lender);
        require(State == StateType.OfferPlaced);

        State = StateType.LenderAccepted;

        emit OfferAccepted(user);
    }

    // reject offer [lender|borrower]
    function RejectOffer(address user) public {
        require(msg.sender == _owner);
        require(user == Lender || user == Borrower);
        require(State == StateType.OfferPlaced);

        Borrower = 0x0000000000000000000000000000000000000000;
        State = StateType.Available;

        emit OfferRejected(user);
    }

    // sends payment with required evidence attached [lender|borrower]
    function SendPayment(
        address user,
        address receiver,
        uint256 paymentNumber,
        uint256 amount,
        string memory evidence
    ) public {
        require(msg.sender == _owner);
        require(
            (user == Lender && receiver == Borrower) ||
                (user == Borrower && receiver == Lender)
        ); // require sender is borrower and receiver is lender or vice-versa
        require(State == StateType.Active); // require that it is an active contract
        require(amount != 0); // require payment amount is not 0

        Balance = Balance - amount;

        // send evidence for counterparty validation, initialy unverified
        Evidences[paymentNumber] = Evidence(
            user,
            evidence,
            EvidenceStatus.Unverified
        );

        State = StateType.AwaitingValidation; // set state to awaiting validation

        emit PaymentSent(
            user,
            receiver,
            amount,
            paymentNumber,
            Evidences[paymentNumber]
        );
    }

    function GetEvidence(uint256 paymentNumber) public view returns (Evidence memory) {
        require(paymentNumber <= PaymentNumber);

        return Evidences[paymentNumber];
    }

    function ValidateEvidence(address user, uint256 paymentNumber)
        public
        payable
    {
        require(msg.sender == _owner);
        require(
            (user == Borrower && Evidences[paymentNumber].sender == Lender) ||
                (user == Lender && Evidences[paymentNumber].sender == Borrower)
        );
        require(State == StateType.AwaitingValidation);

        // validate from website, validation code is stored encrypted in the blockchain
        // encryption is only lifted by having the decryption key that is server unique
        // after some checks, validate...
        Evidences[paymentNumber].evidenceStatus = EvidenceStatus.Valid;

        State = StateType.Active; // set loan state back to active

        emit PaymentValidated(user, paymentNumber, Evidences[paymentNumber]);
    }

    /**
     * EVENTS
     **/
    event Received(address sender, uint256 amount);

    event ContractModified(
        address sender,
        uint256 amount,
        uint256 interest,
        uint256 repaymentPeriod
    );
    event OfferPlaced(
        address sender,
        uint256 offerAmount,
        uint256 offerInterestRate,
        uint256 offerRepaymentPeriod
    );
    event PaymentSent(
        address sender,
        address receiver,
        uint256 amount,
        uint256 paymentNumber,
        Evidence evidence
    );
    event PaymentValidated(
        address sender,
        uint256 paymentNumber,
        Evidence evidence
    );
    event BorrowerConfirmed(address sender);
    event OfferAccepted(address sender);
    event OfferRejected(address sender);
    

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
            Evidence[] memory,
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
            Evidences,
            State
        );
    }
}
