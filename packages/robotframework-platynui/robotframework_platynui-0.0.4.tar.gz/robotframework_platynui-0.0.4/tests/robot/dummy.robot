*** Settings ***
Library     PlatynUI


*** Test Cases ***
first
    Type Keys    /Pane[ends-with(@Name, 'Word - \\\\Remote') and @ClassName='Transparent Windows Client']    <Alt+F4>
    Type Keys
    ...    /Pane[ends-with(@Name, 'Word - \\\\Remote') and @ClassName='Transparent Windows Client']/Pane
    ...    <Escape>
