using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[StructLayout(LayoutKind.Sequential, Pack = 8)]
public struct UiaChangeInfo
{
    public int uiaId;

    [MarshalAs(UnmanagedType.Struct)]
    public object payload;

    [MarshalAs(UnmanagedType.Struct)]
    public object extraInfo;
}
