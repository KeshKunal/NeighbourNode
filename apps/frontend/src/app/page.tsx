export default function Home() {
  return (
    <div className="container mx-auto px-4 py-12 flex flex-col items-center justify-center flex-1 text-center">
      <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-4 text-foreground">
        Welcome to NeighbourNode
      </h1>
      <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mb-8">
        The autonomous, hyper-local sharing economy platform. Browse items, visualize locations, and trigger AI agent workflows seamlessly.
      </p>
      <div className="flex gap-4">
        <a href="/dashboard" className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-8 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50">
          Go to Dashboard
        </a>
        <a href="#catalog" className="inline-flex h-10 items-center justify-center rounded-md border border-input bg-background px-8 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50">
          Browse Catalog
        </a>
      </div>
    </div>
  );
}
