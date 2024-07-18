*** Settings ***
Library     PlatynUI


*** Test Cases ***
# first
#    Ensure Exists    /Pane[ends-with(@Name, 'Word - \\\\Remote') and @ClassName='Transparent Windows Client']    30s

#    Type Keys    /Pane[ends-with(@Name, 'Word - \\\\Remote') and @ClassName='Transparent Windows Client']    <Alt+F4>
#    Type Keys
#    ...    /Pane[ends-with(@Name, 'Word - \\\\Remote') and @ClassName='Transparent Windows Client']
#    ...    <Escape>

first
    Ensure Exists    Window[@Name='Rechner']    30s

    Type Keys    Window[@Name='Rechner']    <Alt+F4>
