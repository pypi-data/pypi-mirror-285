namespace PlatynUI.Technology.UiAutomation.Client;

public enum ProviderOptions
{
    ProviderOptions_ClientSideProvider = 1,
    ProviderOptions_ServerSideProvider = 2,
    ProviderOptions_NonClientAreaProvider = 4,
    ProviderOptions_OverrideProvider = 8,
    ProviderOptions_ProviderOwnsSetFocus = 16, // 0x00000010
    ProviderOptions_UseComThreading = 32, // 0x00000020
    ProviderOptions_RefuseNonClientSupport = 64, // 0x00000040
    ProviderOptions_HasNativeIAccessible = 128, // 0x00000080
    ProviderOptions_UseClientCoordinates = 256, // 0x00000100
}
