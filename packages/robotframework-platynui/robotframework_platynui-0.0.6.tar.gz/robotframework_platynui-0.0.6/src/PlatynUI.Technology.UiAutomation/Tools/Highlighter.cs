using System.Runtime.InteropServices;
using Windows.Win32;
using Windows.Win32.UI.HiDpi;
using Windows.Win32.UI.WindowsAndMessaging;
using Timer = System.Timers.Timer;

namespace PlatynUI.Technology.UiAutomation.Tools;

public class Highlighter : IDisposable
{
    private const int Gap = 1;
    private const int Width = 3;

    private Thread? _thread;
    private readonly bool _autoHide;
    private readonly int _autoHideTimeout;

    private Rect _area;

    private bool _disposed;

    private HighlightHolder? _highlightHolder;
    private Timer? _timer;

    private readonly AutoResetEvent _holderCreatedEvent = new(false);

    public Highlighter(bool autoHide = true, int autoHideTimeout = 2000)
    {
        _autoHide = autoHide;
        _autoHideTimeout = autoHideTimeout;

        StartWndThread();

        _holderCreatedEvent.WaitOne(5000);
    }

    protected void StartWndThread()
    {
        if (_thread == null)
        {
            _thread = new Thread(() =>
            {
                //Thread.CurrentThread.Name = "HighlighterThread";

#pragma warning disable CA1416 // Validate platform compatibility

                try
                {
                    PInvoke.SetThreadDpiAwarenessContext(
                        DPI_AWARENESS_CONTEXT.DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
                    );
                }
                catch (EntryPointNotFoundException)
                {
                    System.Diagnostics.Debug.WriteLine("SetThreadDpiAwarenessContext not found");
                }

#pragma warning restore CA1416 // Validate platform compatibility

                _highlightHolder = new HighlightHolder();

                _holderCreatedEvent.Set();

                while (PInvoke.GetMessage(out MSG msg, default, 0, 0))
                {
                    PInvoke.TranslateMessage(msg);
                    PInvoke.DispatchMessage(msg);
                }
            })
            {
                IsBackground = true,
                Name = "HighlighterThread"
            };

            _thread.Start();
        }
    }

    public Rect Area
    {
        get => _area;
        set
        {
            if (value == Rect.Empty)
            {
                return;
            }

            _area = value;

            if (_highlightHolder == null)
            {
                return;
            }

            var r = _area;

            _highlightHolder.Left.Position = new Rect(
                r.X - Gap - Width,
                r.Y - Gap - Width,
                Width,
                r.Height + (2 * Gap) + (2 * Width)
            );
            _highlightHolder.Top.Position = new Rect(
                r.X - Gap - Width,
                r.Y - Gap - Width,
                r.Width + (Gap * 2) + (Width * 2),
                Width
            );
            _highlightHolder.Right.Position = new Rect(
                r.X + r.Width + Gap,
                r.Y - Gap - Width,
                Width,
                r.Height + (2 * Gap) + (2 * Width)
            );
            _highlightHolder.Bottom.Position = new Rect(
                r.X - Gap - Width,
                r.Y + r.Height + Gap,
                r.Width + (Gap * 2) + (Width * 2),
                Width
            );
        }
    }

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    ~Highlighter()
    {
        Dispose(false);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (_disposed)
        {
            return;
        }

        if (disposing)
        {
            if (_timer != null)
            {
                _timer.Stop();
                _timer.Dispose();
            }

            _highlightHolder?.Dispose();
        }

        _disposed = true;
    }

    public void Hide()
    {
        _highlightHolder?.Top.Hide();
        _highlightHolder?.Left.Hide();
        _highlightHolder?.Right.Hide();
        _highlightHolder?.Bottom.Hide();
    }

    public void Close()
    {
        _highlightHolder?.Top.Close();
        _highlightHolder?.Left.Close();
        _highlightHolder?.Right.Close();
        _highlightHolder?.Bottom.Close();
    }

    public void Show()
    {
        Show(Rect.Empty, _autoHide, _autoHideTimeout);
    }

    public void Show(Rect r)
    {
        Show(r, _autoHide, _autoHideTimeout);
    }

    public void Show(int timeout)
    {
        Show(Rect.Empty, true, timeout);
    }

    public void Show(Rect r, int timeout)
    {
        Show(r, true, timeout);
    }

    public void Show(bool timed)
    {
        Show(Rect.Empty, timed, _autoHideTimeout);
    }

    public void Show(Rect r, bool timed)
    {
        Show(r, timed, _autoHideTimeout);
    }

    public void Show(Rect r, bool timed, int timeout)
    {
        Area = r;
        _highlightHolder?.Top.Show();
        _highlightHolder?.Left.Show();
        _highlightHolder?.Right.Show();
        _highlightHolder?.Bottom.Show();

        if (timed && timeout > 0)
        {
            if (_timer == null)
            {
                _timer = new Timer(timeout) { AutoReset = false };
                _timer.Elapsed += (sender, args) =>
                {
                    Hide();
                };
            }
            else
            {
                _timer.Stop();
            }

            _timer.Start();
        }
    }

    private sealed class HighlightHolder : IDisposable
    {
        public readonly Line Bottom = new();

        public readonly Line Left = new();

        public readonly Line Right = new();

        public readonly Line Top = new();

        private bool _disposed;

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        ~HighlightHolder()
        {
            Dispose(false);
        }

        private void Dispose(bool disposing)
        {
            if (_disposed)
            {
                return;
            }

            if (disposing)
            {
                Top.Dispose();
                Left.Dispose();
                Right.Dispose();
                Bottom.Dispose();
            }

            _disposed = true;
        }
    }
}
