using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[StructLayout(LayoutKind.Sequential, Pack = 4)]
#pragma warning disable IDE1006 // Naming Styles
public struct tagRECT
#pragma warning restore IDE1006 // Naming Styles
{
    public int left;
    public int top;
    public int right;
    public int bottom;
}
