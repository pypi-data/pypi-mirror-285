using System.Runtime.InteropServices;
using Windows.Win32;
using Windows.Win32.UI.Input.KeyboardAndMouse;

namespace PlatynUI.Technology.UiAutomation;

public class VirtualKey
{
    internal static readonly IDictionary<string, VirtualKey> Keys = new Dictionary<string, VirtualKey>(
        StringComparer.OrdinalIgnoreCase
    );

    public static readonly VirtualKey Back = new(VIRTUAL_KEY.VK_BACK);

    public static readonly VirtualKey Tab = new(VIRTUAL_KEY.VK_TAB);

    public static readonly VirtualKey Clear = new(VIRTUAL_KEY.VK_CLEAR);

    public static readonly VirtualKey Return = new(VIRTUAL_KEY.VK_RETURN);

    public static readonly VirtualKey Enter = new(VIRTUAL_KEY.VK_RETURN, true);

    public static readonly VirtualKey Shift = new(VIRTUAL_KEY.VK_SHIFT);

    public static readonly VirtualKey Control = new(VIRTUAL_KEY.VK_CONTROL);

    public static readonly VirtualKey Ctrl = new(VIRTUAL_KEY.VK_CONTROL);

    public static readonly VirtualKey Menu = new(VIRTUAL_KEY.VK_MENU);

    public static readonly VirtualKey Alt = new(Menu);

    public static readonly VirtualKey AltGr = new(Control, Menu);

    public static readonly VirtualKey Pause = new(VIRTUAL_KEY.VK_PAUSE);

    public static readonly VirtualKey Capital = new(VIRTUAL_KEY.VK_CAPITAL);

    // TODO Keycodes
    //    KANA = 0x15,
    //    HANGEUL = 0x15,  // old name - should be here for compatibility
    //    HANGUL = 0x15,
    //    JUNJA = 0x17,
    //    FINAL = 0x18,
    //    HANJA = 0x19,
    //    KANJI = 0x19,




    public static readonly VirtualKey Escape = new(VIRTUAL_KEY.VK_ESCAPE);

    // TODO Keycodes
    //    CONVERT = 0x1C,
    //    NONCONVERT = 0x1D,
    //    ACCEPT = 0x1E,
    //    MODECHANGE = 0x1F




    public static readonly VirtualKey Space = new(VIRTUAL_KEY.VK_SPACE);

    public static readonly VirtualKey Prior = new(VIRTUAL_KEY.VK_PRIOR, true);

    public static readonly VirtualKey Next = new(VIRTUAL_KEY.VK_NEXT, true);

    public static readonly VirtualKey PageUp = Prior;

    public static readonly VirtualKey PageDown = Next;

    public static readonly VirtualKey End = new(VIRTUAL_KEY.VK_END, true);

    public static readonly VirtualKey Home = new(VIRTUAL_KEY.VK_HOME, true);

    public static readonly VirtualKey Left = new(VIRTUAL_KEY.VK_LEFT, true);

    public static readonly VirtualKey Up = new(VIRTUAL_KEY.VK_UP, true);

    public static readonly VirtualKey Right = new(VIRTUAL_KEY.VK_RIGHT, true);

    public static readonly VirtualKey Down = new(VIRTUAL_KEY.VK_DOWN, true);

    public static readonly VirtualKey Select = new(VIRTUAL_KEY.VK_SELECT);

    public static readonly VirtualKey Print = new(VIRTUAL_KEY.VK_PRINT);

    public static readonly VirtualKey Execute = new(VIRTUAL_KEY.VK_EXECUTE);

    public static readonly VirtualKey Snapshot = new(VIRTUAL_KEY.VK_SNAPSHOT);

    public static readonly VirtualKey Insert = new(VIRTUAL_KEY.VK_INSERT, true);

    public static readonly VirtualKey Delete = new(VIRTUAL_KEY.VK_DELETE, true);

    public static readonly VirtualKey Help = new(VIRTUAL_KEY.VK_HELP);

    public static readonly VirtualKey Lwin = new(VIRTUAL_KEY.VK_LWIN);

    public static readonly VirtualKey Rwin = new(VIRTUAL_KEY.VK_RWIN);

    public static readonly VirtualKey Apps = new(VIRTUAL_KEY.VK_APPS);

    public static readonly VirtualKey Sleep = new(VIRTUAL_KEY.VK_SLEEP);

    public static readonly VirtualKey Numpad0 = new(VIRTUAL_KEY.VK_NUMPAD0);

    public static readonly VirtualKey Numpad1 = new(VIRTUAL_KEY.VK_NUMPAD1);

    public static readonly VirtualKey Numpad2 = new(VIRTUAL_KEY.VK_NUMPAD2);

    public static readonly VirtualKey Numpad3 = new(VIRTUAL_KEY.VK_NUMPAD3);

    public static readonly VirtualKey Numpad4 = new(VIRTUAL_KEY.VK_NUMPAD4);

    public static readonly VirtualKey Numpad5 = new(VIRTUAL_KEY.VK_NUMPAD5);

    public static readonly VirtualKey Numpad6 = new(VIRTUAL_KEY.VK_NUMPAD6);

    public static readonly VirtualKey Numpad7 = new(VIRTUAL_KEY.VK_NUMPAD7);

    public static readonly VirtualKey Numpad8 = new(VIRTUAL_KEY.VK_NUMPAD8);

    public static readonly VirtualKey Numpad9 = new(VIRTUAL_KEY.VK_NUMPAD9);

    public static readonly VirtualKey Multiply = new(VIRTUAL_KEY.VK_MULTIPLY);

    public static readonly VirtualKey Add = new(VIRTUAL_KEY.VK_ADD);

    public static readonly VirtualKey Separator = new(VIRTUAL_KEY.VK_SEPARATOR);

    public static readonly VirtualKey Subtract = new(VIRTUAL_KEY.VK_SUBTRACT);

    public static readonly VirtualKey Decimal = new(VIRTUAL_KEY.VK_DECIMAL);

    public static readonly VirtualKey Divide = new(VIRTUAL_KEY.VK_DIVIDE);

    public static readonly VirtualKey F1 = new(VIRTUAL_KEY.VK_F1);

    public static readonly VirtualKey F2 = new(VIRTUAL_KEY.VK_F2);

    public static readonly VirtualKey F3 = new(VIRTUAL_KEY.VK_F3);

    public static readonly VirtualKey F4 = new(VIRTUAL_KEY.VK_F4);

    public static readonly VirtualKey F5 = new(VIRTUAL_KEY.VK_F5);

    public static readonly VirtualKey F6 = new(VIRTUAL_KEY.VK_F6);

    public static readonly VirtualKey F7 = new(VIRTUAL_KEY.VK_F7);

    public static readonly VirtualKey F8 = new(VIRTUAL_KEY.VK_F8);

    public static readonly VirtualKey F9 = new(VIRTUAL_KEY.VK_F9);

    public static readonly VirtualKey F10 = new(VIRTUAL_KEY.VK_F10);

    public static readonly VirtualKey F11 = new(VIRTUAL_KEY.VK_F11);

    public static readonly VirtualKey F12 = new(VIRTUAL_KEY.VK_F12);

    public static readonly VirtualKey F13 = new(VIRTUAL_KEY.VK_F13);

    public static readonly VirtualKey F14 = new(VIRTUAL_KEY.VK_F14);

    public static readonly VirtualKey F15 = new(VIRTUAL_KEY.VK_F15);

    public static readonly VirtualKey F16 = new(VIRTUAL_KEY.VK_F16);

    public static readonly VirtualKey F17 = new(VIRTUAL_KEY.VK_F17);

    public static readonly VirtualKey F18 = new(VIRTUAL_KEY.VK_F18);

    public static readonly VirtualKey F19 = new(VIRTUAL_KEY.VK_F19);

    public static readonly VirtualKey F20 = new(VIRTUAL_KEY.VK_F20);

    public static readonly VirtualKey F21 = new(VIRTUAL_KEY.VK_F21);

    public static readonly VirtualKey F22 = new(VIRTUAL_KEY.VK_F22);

    public static readonly VirtualKey F23 = new(VIRTUAL_KEY.VK_F23);

    public static readonly VirtualKey F24 = new(VIRTUAL_KEY.VK_F24);

    public static readonly VirtualKey Numlock = new(VIRTUAL_KEY.VK_NUMLOCK);

    public static readonly VirtualKey Scroll = new(VIRTUAL_KEY.VK_SCROLL);

    public static readonly VirtualKey Lshift = new(VIRTUAL_KEY.VK_LSHIFT);

    public static readonly VirtualKey Rshift = new(VIRTUAL_KEY.VK_RSHIFT);

    public static readonly VirtualKey Lcontrol = new(VIRTUAL_KEY.VK_LCONTROL);

    public static readonly VirtualKey Rcontrol = new(VIRTUAL_KEY.VK_RCONTROL);

    public static readonly VirtualKey Lmenu = new(VIRTUAL_KEY.VK_LMENU);

    public static readonly VirtualKey Rmenu = new(VIRTUAL_KEY.VK_RMENU);

    public static readonly VirtualKey BrowserBack = new(VIRTUAL_KEY.VK_BROWSER_BACK);

    public static readonly VirtualKey BrowserForward = new(VIRTUAL_KEY.VK_BROWSER_FORWARD);

    public static readonly VirtualKey BrowserRefresh = new(VIRTUAL_KEY.VK_BROWSER_REFRESH);

    public static readonly VirtualKey BrowserStop = new(VIRTUAL_KEY.VK_BROWSER_STOP);

    public static readonly VirtualKey BrowserSearch = new(VIRTUAL_KEY.VK_BROWSER_SEARCH);

    public static readonly VirtualKey BrowserFavorites = new(VIRTUAL_KEY.VK_BROWSER_FAVORITES);

    public static readonly VirtualKey BrowserHome = new(VIRTUAL_KEY.VK_BROWSER_HOME);

    public static readonly VirtualKey VolumeMute = new(VIRTUAL_KEY.VK_VOLUME_MUTE);

    public static readonly VirtualKey VolumeDown = new(VIRTUAL_KEY.VK_VOLUME_DOWN);

    public static readonly VirtualKey VolumeUp = new(VIRTUAL_KEY.VK_VOLUME_UP);

    public static readonly VirtualKey MediaNextTrack = new(VIRTUAL_KEY.VK_MEDIA_NEXT_TRACK);

    public static readonly VirtualKey MediaPrevTrack = new(VIRTUAL_KEY.VK_MEDIA_PREV_TRACK);

    public static readonly VirtualKey MediaStop = new(VIRTUAL_KEY.VK_MEDIA_STOP);

    public static readonly VirtualKey MediaPlayPause = new(VIRTUAL_KEY.VK_MEDIA_PLAY_PAUSE);

    public static readonly VirtualKey LaunchMail = new(VIRTUAL_KEY.VK_LAUNCH_MAIL);

    public static readonly VirtualKey LaunchMediaSelect = new(VIRTUAL_KEY.VK_LAUNCH_MEDIA_SELECT);

    public static readonly VirtualKey LaunchApp1 = new(VIRTUAL_KEY.VK_LAUNCH_APP1);

    public static readonly VirtualKey LaunchApp2 = new(VIRTUAL_KEY.VK_LAUNCH_APP2);

    /* TODO Keycodes
       OEM_1 = 0xBA,   // ';:' for US
       OEM_PLUS = 0xBB,   // '+' any country
       OEM_COMMA = 0xBC,   // ',' any country
       OEM_MINUS = 0xBD,   // '-' any country
       OEM_PERIOD = 0xBE,   // '.' any country
       OEM_2 = 0xBF,   // '/?' for US
       OEM_3 = 0xC0,   // '`~' for US
       //
       // 0xC1 - 0xD7 : reserved
       //
       //
       // 0xD8 - 0xDA : unassigned
       //
       OEM_4 = 0xDB,  //  '[{' for US
       OEM_5 = 0xDC,  //  '\|' for US
       OEM_6 = 0xDD,  //  ']}' for US
       OEM_7 = 0xDE,  //  ''"' for US
       OEM_8 = 0xDF
   */

    static VirtualKey()
    {
        foreach (
            var fieldInfo in typeof(VirtualKey)
                .GetFields()
                .Where(fieldInfo => fieldInfo.IsStatic && fieldInfo.FieldType == typeof(VirtualKey))
        )
        {
            Keys.Add(fieldInfo.Name, fieldInfo.GetValue(null) as VirtualKey ?? throw new InvalidOperationException());
        }
    }

    internal VirtualKey(VIRTUAL_KEY vk, bool extended = false)
    {
        Value = [(ushort)vk];
        Extended = [extended];
    }

    internal VirtualKey(params VirtualKey[] value)
    {
        Value = value.SelectMany(v => v.Value).ToArray();
        Extended = value.SelectMany(v => v.Extended).ToArray();
    }

    internal VirtualKey(params ushort[] value)
    {
        Value = value;
        Extended = new bool[value.Length];
    }

    internal ushort[] Value { get; set; }

    internal bool[] Extended { get; set; }

    public override string ToString()
    {
        return string.Join(" + ", Value.Select((v, i) => (Extended[i] ? "Extended " : "") + v));
    }

    public override int GetHashCode()
    {
        return Value.GetHashCode() ^ Extended.GetHashCode();
    }

    public override bool Equals(object? obj)
    {
        if (obj is VirtualKey vk)
        {
            return Value.SequenceEqual(vk.Value) && Extended.SequenceEqual(vk.Extended);
        }
        return base.Equals(obj);
    }
}

public class Keycode(object? key, object? code, bool valid, string? errorText)
{
    public object? Key { get; } = key;
    public object? Code { get; } = code;
    public bool Valid { get; } = valid;
    public string? ErrorText { get; } = errorText;

    public override string ToString()
    {
        return $"{Key} - {Code} - {Valid} - {ErrorText}";
    }
}

public static class KeyboardDevice
{
    private static VirtualKey ToVirtualKeyCodes(char c)
    {
        var result = new List<ushort>();
        if (c == '\n')
        {
            return VirtualKey.Return;
        }

        var key = PInvoke.VkKeyScan(c);

        if (key == -1)
        {
            return new VirtualKey(c);
        }

        // SHIFT
        if ((key & 0x0100) != 0)
        {
            result.AddRange(VirtualKey.Shift.Value);
        }

        // SHIFT
        if ((key & 0x0200) != 0)
        {
            result.AddRange(VirtualKey.Control.Value);
        }

        // ALT
        if ((key & 0x0400) != 0)
        {
            result.AddRange(VirtualKey.Menu.Value);
        }

        // TODO: HANAKU
        /*
            if ((key & 0x0800) != 0) {
            result.add(VirtualKey.getValue());
            }
        *
        */

        result.Add((ushort)(key & 0xff));
        return new VirtualKey(result.ToArray());
    }

    public static Keycode KeyToKeyCode(object? key)
    {
        if (key == null)
            return new Keycode(key, null, false, "Key is null");

        switch (key)
        {
            case string keystr:
            {
                if (VirtualKey.Keys.TryGetValue(keystr, out var virtualKey))
                    return new Keycode(key, virtualKey, true, null);

                if (keystr.Length == 1 && keystr[0] <= '\x007f')
                {
                    return new Keycode(key, ToVirtualKeyCodes(keystr[0]), true, null);
                }

                return new Keycode(key, key, true, null);
            }

            case char keychar:
                return new Keycode(key, ToVirtualKeyCodes(keychar), true, null);
        }

        return new Keycode(key, null, false, "Unknown key");
    }

    public static unsafe bool SendKeyCode(object keyCode, bool pressed)
    {
        if (keyCode is VirtualKey virtualKey)
        {
            var keys = virtualKey.Value.Select((x, i) => new { Value = x, Extended = virtualKey.Extended[i] });
            if (!pressed)
            {
                keys = keys.Reverse();
            }
            foreach (var it in keys)
            {
                var inputs = new INPUT
                {
                    type = INPUT_TYPE.INPUT_KEYBOARD,
                    Anonymous =
                    {
                        ki =
                        {
                            wVk = (VIRTUAL_KEY)it.Value,
                            wScan = (ushort)
                                PInvoke.MapVirtualKeyEx(it.Value, MAP_VIRTUAL_KEY_TYPE.MAPVK_VK_TO_VSC, HKL.Null),
                            dwFlags =
                                (it.Extended ? KEYBD_EVENT_FLAGS.KEYEVENTF_EXTENDEDKEY : 0)
                                | (pressed ? 0 : KEYBD_EVENT_FLAGS.KEYEVENTF_KEYUP),
                        }
                    }
                };

                PInvoke.SendInput(1, &inputs, Marshal.SizeOf<INPUT>());
            }

            return true;
        }
        else if (keyCode is string keystr)
        {
            var keys = keystr.Select((x) => new { Value = x });
            if (!pressed)
            {
                keys = keys.Reverse();
            }

            var inputs = new List<INPUT>();
            foreach (var it in keys)
            {
                inputs.Add(
                    new INPUT
                    {
                        type = INPUT_TYPE.INPUT_KEYBOARD,
                        Anonymous =
                        {
                            ki =
                            {
                                wVk = 0,
                                wScan = it.Value,
                                dwFlags =
                                    KEYBD_EVENT_FLAGS.KEYEVENTF_UNICODE
                                    | (pressed ? 0 : KEYBD_EVENT_FLAGS.KEYEVENTF_KEYUP),
                            }
                        }
                    }
                );
                var inpArray = inputs.ToArray();
                fixed (INPUT* inpArrayPtr = inpArray)
                {
                    PInvoke.SendInput((uint)inpArray.Length, inpArrayPtr, Marshal.SizeOf<INPUT>());
                }
            }

            return true;
        }

        return false;
    }
}
