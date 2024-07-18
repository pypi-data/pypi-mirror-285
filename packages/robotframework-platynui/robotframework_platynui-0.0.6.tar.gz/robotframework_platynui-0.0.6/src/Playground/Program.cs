// using PlatynUI.Technology.UiAutomation;
// using PlatynUI.Technology.UiAutomation.Core;

// //Console.OutputEncoding = System.Text.Encoding.Unicode;
// var stopwatch = new System.Diagnostics.Stopwatch();

// stopwatch.Start();
// //var result = Finder.EnumAllElements(null, "Window[@Name='WPF Test Application']//DataGrid//Text/../../../../..");
// var result = Finder.Evaluate(null, "namespace-uri(/*)");
// Console.WriteLine(stopwatch.Elapsed);
// stopwatch.Restart();
// foreach (var item in result)
// {
//     Console.WriteLine(stopwatch.Elapsed);
//     Console.WriteLine($"{item} {item?.GetType()}");
//     stopwatch.Restart();
// }


// //var result = Finder.FindAllElements(null, "Application[@Name='Calculator']");
// //var result = Finder.FindAllElements(null, "//*[@Name='Start']");
// //var result = Finder.FindAllElements(null, "/app:Application");

// Console.WriteLine(result);

// // var result = Finder.Evaluate(null, "1+2");

// // foreach (var item in result)
// // {
// //     Console.WriteLine($"{item.GetDisplayName()} {item?.GetType()}");
// // }

Console.WriteLine(OperatingSystem.IsWindows());
