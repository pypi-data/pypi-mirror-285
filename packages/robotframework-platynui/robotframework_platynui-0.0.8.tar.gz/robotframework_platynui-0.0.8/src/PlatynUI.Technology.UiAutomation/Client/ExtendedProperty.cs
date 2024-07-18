using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[StructLayout(LayoutKind.Sequential, Pack = 8)]
public struct ExtendedProperty
{
    [MarshalAs(UnmanagedType.BStr)]
    public string PropertyName;

    [MarshalAs(UnmanagedType.BStr)]
    public string PropertyValue;
}
