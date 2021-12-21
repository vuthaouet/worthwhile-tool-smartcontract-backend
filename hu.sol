{
  "contract": "integer_overflow_minimal",
  "sourceLanguage": "Solidity",
  "analysis": {
    "17": [
      {
        "level": "warning",
        "tool": [
          "mythril",
          "oyente"
        ],
        "snippet": {
          "text": "count -= input"
        },
        "fullDescription": "A possible integer underflow exists in the function `run(uint256)`.\n
        The subtraction may result in a value < 0.",
        "name": "ArithmeticVulnerability"
      }
    ]
  },
  "listLine": [
    17
  ],
  "rules": [
    {
      "id": "Arithmetic_5",
      "fullDescription": {
        "text": "A possible integer underflow exists in the function `run(uint256)`.\nThe subtraction may result in a value < 0."
      },
      "name": "ArithmeticVulnerability",
      "shortDescription": {
        "text": "Integer Underflow"
      }
    }
  ]
}