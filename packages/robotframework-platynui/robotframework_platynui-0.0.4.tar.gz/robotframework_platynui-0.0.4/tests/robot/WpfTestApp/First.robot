*** Settings ***
Library         PlatynUI
Variables       mapping.py


*** Test Cases ***
first
    Activate   /Window[@AutomationId='Shell' and @ProcessName='WpfTestApp']//Button[@AutomationId='DoSomethingOther']
    Click   /Window[@AutomationId='Shell' and @ProcessName='WpfTestApp']//Button[@AutomationId='DoSomethingOther']
