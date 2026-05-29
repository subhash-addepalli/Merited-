export function LoadingSkeleton() {
  return (
    <div className="w-full max-w-2xl mx-auto animate-fade-in space-y-4">
      {/* Header skeleton */}
      <div className="card p-6 flex items-center gap-4">
        <div className="w-16 h-16 rounded-full shimmer" />
        <div className="flex-1 space-y-2">
          <div className="h-5 w-40 rounded-lg shimmer" />
          <div className="h-3.5 w-24 rounded-lg shimmer" />
        </div>
        <div className="h-7 w-28 rounded-full shimmer" />
      </div>

      {/* Scores skeleton */}
      <div className="card p-6 space-y-5">
        <div className="h-4 w-32 rounded shimmer" />
        <div className="space-y-4">
          {[1, 2].map((i) => (
            <div key={i} className="space-y-2">
              <div className="flex justify-between">
                <div className="h-3.5 w-28 rounded shimmer" />
                <div className="h-3.5 w-10 rounded shimmer" />
              </div>
              <div className="h-2 rounded-full shimmer" />
            </div>
          ))}
        </div>
      </div>

      {/* Project skeleton */}
      <div className="card p-6 space-y-4">
        <div className="h-4 w-24 rounded shimmer" />
        <div className="h-5 w-48 rounded shimmer" />
        <div className="h-3.5 w-full rounded shimmer" />
        <div className="flex gap-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-6 w-20 rounded-full shimmer" />
          ))}
        </div>
      </div>

      {/* Recommendation skeleton */}
      <div className="card p-6 space-y-3">
        <div className="h-4 w-36 rounded shimmer" />
        <div className="h-3.5 w-full rounded shimmer" />
        <div className="h-3.5 w-4/5 rounded shimmer" />
        <div className="h-3.5 w-3/5 rounded shimmer" />
      </div>

      <p className="text-center text-xs text-white/25 font-mono">
        Fetching repositories · Scoring activity · Generating evaluation...
      </p>
    </div>
  );
}
