"use client";

interface Props {
  zoneData: Record<string, number>;
}

export default function CourtHeatmap({ zoneData }: Props) {
  // 3x3 grid zones 1-9
  const zones = Array.from({ length: 9 }, (_, i) => i + 1);
  const maxCount = Math.max(...zones.map((z) => zoneData[z] || 0), 1);

  return (
    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
      <h3 className="text-lg font-semibold mb-4">Court Heatmap</h3>
      <div className="aspect-[3/2] max-w-md mx-auto">
        {/* Court outline */}
        <div className="grid grid-cols-3 grid-rows-3 gap-1 h-full border-2 border-gray-600 rounded-lg overflow-hidden relative">
          {/* Net line */}
          <div className="absolute left-0 right-0 top-1/2 h-0.5 bg-white/30 z-10" />
          {zones.map((zone) => {
            const count = zoneData[zone] || 0;
            const intensity = count / maxCount;
            return (
              <div
                key={zone}
                className="flex items-center justify-center text-sm font-mono relative"
                style={{
                  backgroundColor: `rgba(249, 115, 22, ${intensity * 0.8})`,
                }}
              >
                <span className="text-xs text-gray-300">Z{zone}</span>
                <span className="absolute bottom-0.5 text-[10px] text-gray-400">{count}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
