namespace PlatynUI.Technology.UiAutomation.Tools;

using System;
using System.Runtime.InteropServices;
using Windows.Win32;
using Windows.Win32.Foundation;
using Windows.Win32.UI.WindowsAndMessaging;
using static Windows.Win32.PInvoke;

internal class Line : IDisposable
{
    private static readonly string Classname = "PlatynUI_Technology_UiAutomation_Tools_Line";

    private static readonly WNDPROC MyWndProc = CbWndProc;

    private bool _disposed;

    private HWND _handle;

    private Rect _position;

    private static readonly ushort _lineClassAtom;

    static unsafe Line()
    {
        using var hInst = GetModuleHandle((string?)null);
        fixed (char* pClassname = Classname)
        {
            var lineClassEx = new WNDCLASSEXW
            {
                cbSize = (uint)Marshal.SizeOf<WNDCLASSEXW>(),
                style = WNDCLASS_STYLES.CS_SAVEBITS | WNDCLASS_STYLES.CS_VREDRAW | WNDCLASS_STYLES.CS_HREDRAW,
                lpfnWndProc = MyWndProc,
                hInstance = (HINSTANCE)hInst.DangerousGetHandle(),
                hbrBackground = CreateSolidBrush(new COLORREF(0x000000ff)),
                lpszClassName = pClassname,
            };

            _lineClassAtom = RegisterClassEx(lineClassEx);
        }
    }

    public unsafe Line()
    {
        _handle = CreateWindowEx(
            WINDOW_EX_STYLE.WS_EX_LAYERED
                | WINDOW_EX_STYLE.WS_EX_TRANSPARENT
                | WINDOW_EX_STYLE.WS_EX_TOOLWINDOW
                | WINDOW_EX_STYLE.WS_EX_NOACTIVATE
                | WINDOW_EX_STYLE.WS_EX_TOPMOST,
            Classname,
            string.Empty,
            WINDOW_STYLE.WS_POPUP | WINDOW_STYLE.WS_DISABLED,
            0,
            0,
            0,
            0,
            default,
            default,
            default,
            default
        );

        SetLayeredWindowAttributes(_handle, new COLORREF(0), 255, LAYERED_WINDOW_ATTRIBUTES_FLAGS.LWA_ALPHA);
    }

    public Rect Position
    {
        get => _position;
        set
        {
            _position = value;

            SetWindowPos(
                _handle,
                default,
                (int)_position.X,
                (int)_position.Y,
                (int)_position.Width,
                (int)_position.Height,
                SET_WINDOW_POS_FLAGS.SWP_NOZORDER
                    | SET_WINDOW_POS_FLAGS.SWP_NOACTIVATE
                    | SET_WINDOW_POS_FLAGS.SWP_NOOWNERZORDER
                    | SET_WINDOW_POS_FLAGS.SWP_ASYNCWINDOWPOS
            );
        }
    }

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    private static LRESULT CbWndProc(HWND hWnd, uint msg, WPARAM wParam, LPARAM lParam)
    {
        switch (msg)
        {
            case WM_CLOSE:
                DestroyWindow(hWnd);
                break;
        }

        return DefWindowProc(hWnd, msg, wParam, lParam);
    }

    private void Dispose(bool disposing)
    {
        if (_disposed)
        {
            return;
        }

        if (disposing) { }

        DestroyWindow(_handle);

        _handle = default;

        _disposed = true;
    }

    ~Line()
    {
        Dispose(false);
    }

    internal void Hide()
    {
        SetWindowPos(
            _handle,
            default,
            0,
            0,
            0,
            0,
            SET_WINDOW_POS_FLAGS.SWP_NOSIZE
                | SET_WINDOW_POS_FLAGS.SWP_NOMOVE
                | SET_WINDOW_POS_FLAGS.SWP_NOZORDER
                | SET_WINDOW_POS_FLAGS.SWP_NOACTIVATE
                | SET_WINDOW_POS_FLAGS.SWP_HIDEWINDOW
                | SET_WINDOW_POS_FLAGS.SWP_ASYNCWINDOWPOS
        );
    }

    internal void Close()
    {
        CloseWindow(_handle);
    }

    internal void Show()
    {
        SetWindowPos(
            _handle,
            HWND.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            SET_WINDOW_POS_FLAGS.SWP_NOSIZE
                | SET_WINDOW_POS_FLAGS.SWP_NOMOVE
                | SET_WINDOW_POS_FLAGS.SWP_NOACTIVATE
                | SET_WINDOW_POS_FLAGS.SWP_SHOWWINDOW
                | SET_WINDOW_POS_FLAGS.SWP_ASYNCWINDOWPOS
        );
    }
}
