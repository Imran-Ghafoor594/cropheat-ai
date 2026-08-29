"use client";

import { useEffect, useMemo, useState } from "react";
import { MapContainer, TileLayer, Polygon, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";

interface HeatmapTileFeature {
  properties: { value?: number; average_temperature?: number; tile_id?: number };
  geometry: { type: string; coordinates: number[][][] };
}

interface CropHeatMapProps {
  heatmapData: { map_data?: { features: HeatmapTileFeature[] }; features?: HeatmapTileFeature[] };
  analyticLabel: string;
  center: [number, number];
}

function colorForValue(value: number, min: number, max: number): string {
  const t = max > min ? (value - min) / (max - min) : 0;
  if (t < 0.33) return "#4ADE80";
  if (t < 0.6) return "#FBBF24";
  if (t < 0.85) return "#FB923C";
  return "#F43F5E";
}

export function CropHeatMap({ heatmapData, analyticLabel, center }: CropHeatMapProps) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const features = heatmapData.map_data?.features ?? heatmapData.features ?? [];
  const values = features.map((f) => f.properties.value ?? f.properties.average_temperature ?? 0);
  const min = values.length ? Math.min(...values) : 0;
  const max = values.length ? Math.max(...values) : 1;

  const polygons = useMemo(
    () =>
      features.map((f, i) => {
        const value = f.properties.value ?? f.properties.average_temperature ?? 0;
        const ring = f.geometry.coordinates[0] ?? [];
        const positions: [number, number][] = ring.map(([lng, lat]) => [lat, lng]);
        return { key: f.properties.tile_id ?? i, positions, value, color: colorForValue(value, min, max) };
      }),
    [features, min, max]
  );

  if (!mounted) {
    return <div className="w-full h-[420px] rounded-2xl bg-surface animate-pulse" />;
  }

  return (
    <div className="relative w-full h-[420px] rounded-2xl overflow-hidden border border-hairline">
      <MapContainer
        center={center}
        zoom={15}
        scrollWheelZoom={false}
        style={{ width: "100%", height: "100%", background: "#0A0D0B" }}
      >
        {/* BUGFIX: CARTO's dark_all basemap started requiring an API key
            (watermark: "API KEY REQUIRED" appeared over every tile), so this
            switches to standard OpenStreetMap tiles -- always free, no key --
            with a CSS filter to approximate the dark theme instead. */}
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          className="map-tiles-dark"
        />
        {polygons.map((p) => (
          <Polygon
            key={p.key}
            positions={p.positions}
            pathOptions={{ color: p.color, fillColor: p.color, fillOpacity: 0.55, weight: 1 }}
          >
            <Tooltip direction="top" opacity={0.95}>
              {analyticLabel}: {p.value.toFixed(1)}
            </Tooltip>
          </Polygon>
        ))}
      </MapContainer>
      <div className="absolute bottom-3 left-3 glass-panel rounded-lg px-3 py-2 text-[10px] text-ink-muted font-mono z-[1000]">
        {features.length} tiles · {analyticLabel}
      </div>
    </div>
  );
}