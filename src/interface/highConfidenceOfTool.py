Hight_Confidence_Vulnerabilities_Of_Mythril = [
    "ReentrancyVulnerability",
    "ArithmeticVulnerability",
    "AccessControlVulnerability"
]
Hight_Confidence_Vulnerabilities_Of_Slither = [
    "UncheckedLowCallsVulnerability",
    "DenialServiceVulnerability",
    "AccessControlVulnerability",
    "IgnoreVulnerability"
]
Hight_Confidence_Vulnerabilities_Of_Oyente = [
    "TimeManipulationVulnerability",
    "ReentrancyVulnerability"
]
Hight_Confidence_Vulnerabilities_Of_Honeybadger = [
    "ReentrancyVulnerability",
    "ArithmeticVulnerability"
]
List_Hight_Confidence_Vulnerabilities = {
    "mythril" : Hight_Confidence_Vulnerabilities_Of_Mythril,
    "slither" : Hight_Confidence_Vulnerabilities_Of_Slither,
    "oyente" : Hight_Confidence_Vulnerabilities_Of_Oyente,
    "honeybadger" : Hight_Confidence_Vulnerabilities_Of_Honeybadger,
}
Default_Count_Leve_Vulnerabilities ={ "warning" : 0,"error":0,"note":0,"none":0}