using System.ComponentModel.Composition;
using System.ComponentModel.Composition.Hosting;
using System.ComponentModel.Composition.ReflectionModel;
using System.IO;
using System.Reflection;
using System.Windows;
using Caliburn.Micro;

namespace PlatynUI.Technology.UiAutomation.Spy;

public class Bootstrapper : BootstrapperBase, IDisposable
{
    private static readonly ILog Logger;

    protected CompositionContainer? Container;

    static Bootstrapper()
    {
#if TRACE
        //Trace.Listeners.Add(new OutputWindowTraceListener("Trace Output"));
#endif

#if DEBUG
        LogManager.GetLog = type => new DebugLogger(type);
#endif
        Logger = LogManager.GetLog(typeof(Bootstrapper));
    }

    public Bootstrapper()
        : this(true) { }

    public Bootstrapper(bool useApplication)
        : base(useApplication)
    {
        Initialize();
    }

    public virtual IEnumerable<string> ModuleDirectories => new string[] { };

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    protected override void Configure()
    {
        // Add all assemblies to AssemblySource (using a temporary DirectoryCatalog)

        foreach (var d in ModuleDirectories)
        {
            if (!Directory.Exists(d))
            {
                Logger.Info("Module directory '{0}' not exists, skipping", d);
                continue;
            }

            var directoryCatalog = new DirectoryCatalog(d);
            AssemblySource.Instance.AddRange(
                directoryCatalog
                    .Parts.Select(part => ReflectionModelServices.GetPartType(part).Value.Assembly)
                    .Where(assembly => !AssemblySource.Instance.Contains(assembly))
            );
        }

        // Prioritise the executable assembly. This allows the client project to override exports, including IShell.
        // The client project can override SelectAssemblies to choose which assemblies are prioritised.
        var priorityAssemblies = SelectAssemblies().ToList();
        var priorityCatalog = new AggregateCatalog(priorityAssemblies.Select(x => new AssemblyCatalog(x)));
        var priorityProvider = new CatalogExportProvider(priorityCatalog);

        // Now get all other assemblies (excluding the priority assemblies).
        var mainCatalog = new AggregateCatalog(
            AssemblySource
                .Instance.Where(assembly => !priorityAssemblies.Contains(assembly))
                .Select(x => new AssemblyCatalog(x))
        );
        var mainProvider = new CatalogExportProvider(mainCatalog);

        Container = new CompositionContainer(priorityProvider, mainProvider);
        priorityProvider.SourceProvider = Container;
        mainProvider.SourceProvider = Container;

        var batch = new CompositionBatch();

        BindServices(batch);

        batch.AddExportedValue(mainCatalog);

        Container.Compose(batch);
    }

    protected virtual void BindServices(CompositionBatch batch)
    {
        var windowManager = new WindowManager();
        batch.AddExportedValue<IWindowManager>(windowManager);

        batch.AddExportedValue<IEventAggregator>(new EventAggregator());
        batch.AddExportedValue(Container);
    }

    protected override object? GetInstance(Type serviceType, string key)
    {
        // Skip trying to instantiate views since MEF will throw an exception
        if (typeof(UIElement).IsAssignableFrom(serviceType))
        {
            return null;
        }

        var contract = string.IsNullOrEmpty(key) ? AttributedModelServices.GetContractName(serviceType) : key;
        if (Container == null)
        {
            throw new InvalidOperationException("Composition container is not initialized.");
        }
        var exports = Container.GetExports<object>(contract).ToArray();

        if (exports.Any())
        {
            return exports.First().Value;
        }

        throw new Exception($"Could not locate any instances of contract {contract}.");
    }

    protected override IEnumerable<object> GetAllInstances(Type serviceType)
    {
        if (Container == null)
        {
            throw new InvalidOperationException("Composition container is not initialized.");
        }
        return Container.GetExportedValues<object>(AttributedModelServices.GetContractName(serviceType));
    }

    protected override void BuildUp(object instance)
    {
        if (Container == null)
        {
            throw new InvalidOperationException("Composition container is not initialized.");
        }
        Container.SatisfyImportsOnce(instance);
    }

    protected override async void OnStartup(object sender, StartupEventArgs e)
    {
        await DisplayRootViewForAsync<ShellViewModel>();
    }

    protected override IEnumerable<Assembly> SelectAssemblies()
    {
        var entryAssembly = Assembly.GetEntryAssembly();
        if (entryAssembly != null)
        {
            return [entryAssembly];
        }
        return [];
    }

    protected virtual void Dispose(bool disposing)
    {
        if (disposing)
        {
            Container?.Dispose();
        }
    }
}
