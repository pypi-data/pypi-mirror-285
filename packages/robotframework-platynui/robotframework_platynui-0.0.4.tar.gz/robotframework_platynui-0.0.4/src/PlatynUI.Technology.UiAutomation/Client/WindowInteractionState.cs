namespace PlatynUI.Technology.UiAutomation.Client;

public enum WindowInteractionState
{
    WindowInteractionState_Running,
    WindowInteractionState_Closing,
    WindowInteractionState_ReadyForUserInteraction,
    WindowInteractionState_BlockedByModalWindow,
    WindowInteractionState_NotResponding,
}
