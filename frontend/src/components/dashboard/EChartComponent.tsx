import { useEffect, useRef } from "react";
import * as echarts from "echarts";

type EChartsOption = echarts.EChartsOption;

function EChartsComponent({
  option,
  height = 300,
}: {
  option: EChartsOption;
  height?: number;
}) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (chartRef.current) {
      chartInstance.current = echarts.init(chartRef.current);
      chartInstance.current.setOption(option);
    }

    const handleResize = () => {
      chartInstance.current?.resize();
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chartInstance.current?.dispose();
    };
  }, [option]);

  return (
    <div ref={chartRef} style={{ width: "100%", height: `${height}px` }} />
  );
}

export default EChartsComponent;
