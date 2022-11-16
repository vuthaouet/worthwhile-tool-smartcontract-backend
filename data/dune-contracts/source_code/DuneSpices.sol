// SPDX-License-Identifier: MIT
pragma solidity ^0.8.2;

import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20BurnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

/// @custom:security-contact tunogya@qq.com
contract DuneSpices is Initializable, ERC20Upgradeable, ERC20BurnableUpgradeable, OwnableUpgradeable, UUPSUpgradeable {
    // Event of game start
    event startGame(uint256 landID, address avatar, uint256 entryBlock, uint256 exitBlock);
    // Event of game over
    event overGame(uint256 landID, address avatar, uint256 entryBlock, uint256 exitBlock, uint256 vault);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() initializer {}

    function initialize() initializer public {
        __ERC20_init("DuneSpices", "SPICES");
        __ERC20Burnable_init();
        __Ownable_init();
        __UUPSUpgradeable_init();
    }

    // the max number of land ID
    uint256 _maxLandID;

    // expand max of land ID
    function expandLand(uint256 newMaxLandID) public onlyOwner {
        require(newMaxLandID > _maxLandID, "DUNE: can only expand land ID!");
        _maxLandID = newMaxLandID;
    }

    // return the max of land ID
    function maxLandID () public view returns (uint256) {
        return _maxLandID;
    }

    // avatar info
    struct AVATARINFO {
        uint256 landID;         // the land ID which avatar choices to entry, if 0, means had exit the DUNE
        uint256 entryBlock;     // the block number when avatar entry the DUNE, if 0, means had exit the DUNE
        uint256 exitBlock;      // the block number which avatar hope to exit the DUNE.
        uint256 spicesVault;    // the vault of SPICES in avatar body, when you burn SPICES, the vault will added to avatar
    }

    // land info
    struct LANDINFO {
        uint256 nonce;          // the number of avatar minting in this land
    }

    // address of avatar => AVATARINFO
    mapping(address => AVATARINFO) _avatarInfo;

    // get avatar mint info
    function getAvatarInfo(address avatar) public view returns (AVATARINFO memory) {
        return _avatarInfo[avatar];
    }

    // landID => LANDINFO
    mapping(uint256 => LANDINFO) _landInfo;

    // get land info
    function getLandInfo(uint256 landID) public view returns (LANDINFO memory) {
        require(landID <= _maxLandID, "DUNE: LandID is over max land ID!");
        return _landInfo[landID];
    }

    // start the game
    function start(uint256 landID, uint256 exitBlock) public returns (AVATARINFO memory) {
        // check the landID
        require(landID <= _maxLandID, "DUNE: LandID is over max land ID!");
        // check the exitBlock
        require(exitBlock > block.number, "DUNE: ExitBlock is error!");
        // check the avatar
        require(_avatarInfo[msg.sender].landID == 0, "DUNE: You had into the DUNE!");
        // change avatar status
        _avatarInfo[msg.sender].landID = landID;
        _avatarInfo[msg.sender].entryBlock = block.number;
        _avatarInfo[msg.sender].exitBlock = exitBlock;
        // update the land info
        _landInfo[landID].nonce += 1;
        emit startGame(landID, msg.sender, block.number, exitBlock);
        return _avatarInfo[msg.sender];
    }

    // game over
    function over() public {
        // check the avatar info by AVATARINFO
        require(_avatarInfo[msg.sender].landID != 0, "DUNE: You haven't started the game yet");
        // calculated production of spices
        uint256 vault;
        if (block.number >= _avatarInfo[msg.sender].exitBlock) {
            // well done!
            vault = (_avatarInfo[msg.sender].exitBlock - _avatarInfo[msg.sender].entryBlock) * 1 ether;
        } else {
            // give up halfway
            vault = (block.number - _avatarInfo[msg.sender].entryBlock) * 1 ether;
        }
        emit overGame(_avatarInfo[msg.sender].landID, msg.sender, _avatarInfo[msg.sender].entryBlock, block.number, vault);
        // change land info
        _landInfo[_avatarInfo[msg.sender].landID].nonce -= 1;
        // change avatar status, make avatar leave the DUNE
        _avatarInfo[msg.sender].landID = 0;
        _avatarInfo[msg.sender].entryBlock = 0;
        _avatarInfo[msg.sender].exitBlock = 0;
        // mint Spices to avatar address
        _mint(msg.sender, vault);
    }

    function _authorizeUpgrade(address newImplementation)
    internal
    onlyOwner
    override
    {}

    // avatar will take spices
    function takeSpices(address avatar, uint256 amount) public {
        _burn(msg.sender, amount);
        _avatarInfo[avatar].spicesVault += amount;
    }
}
