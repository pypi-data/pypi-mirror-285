using System.Runtime.InteropServices;

#nullable disable
namespace PlatynUI.Technology.UiAutomation.Client;

[StructLayout(LayoutKind.Sequential, Pack = 4)]
#pragma warning disable IDE1006 // Naming Styles
public struct tagPOINT
#pragma warning restore IDE1006 // Naming Styles
{
    public int x;
    public int y;
}
