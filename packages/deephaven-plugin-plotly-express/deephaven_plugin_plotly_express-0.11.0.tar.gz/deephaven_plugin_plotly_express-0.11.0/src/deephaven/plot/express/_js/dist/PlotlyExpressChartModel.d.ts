import type { Layout, Data } from 'plotly.js';
import type { dh as DhType } from '@deephaven/jsapi-types';
import { ChartModel, ChartUtils } from '@deephaven/chart';
import { DownsampleInfo, PlotlyChartWidgetData } from './PlotlyExpressChartUtils';
export declare class PlotlyExpressChartModel extends ChartModel {
    /**
     * The size at which the chart will automatically downsample the data if it can be downsampled.
     * If it cannot be downsampled, but the size is below MAX_FETCH_SIZE,
     * the chart will show a confirmation to fetch the data since it might be a slow operation.
     */
    static AUTO_DOWNSAMPLE_SIZE: number;
    /**
     * The maximum number of items that can be fetched from a table.
     * If a table is larger than this, the chart will not be fetched.
     * This is to prevent the chart from fetching too much data and crashing the browser.
     */
    static MAX_FETCH_SIZE: number;
    static canFetch(table: DhType.Table): boolean;
    constructor(dh: typeof DhType, widget: DhType.Widget, refetch: () => Promise<DhType.Widget>);
    isSubscribed: boolean;
    chartUtils: ChartUtils;
    refetch: () => Promise<DhType.Widget>;
    widget?: DhType.Widget;
    widgetUnsubscribe?: () => void;
    /**
     * Map of table index to Table object.
     */
    tableReferenceMap: Map<number, DhType.Table>;
    /**
     * Map of downsampled table indexes to original Table object.
     */
    downsampleMap: Map<number, DownsampleInfo>;
    /**
     * Map of table index to TableSubscription object.
     */
    tableSubscriptionMap: Map<number, DhType.TableSubscription>;
    /**
     * Map of table index to cleanup function for the subscription.
     */
    subscriptionCleanupMap: Map<number, () => void>;
    /**
     * Map of table index to map of column names to array of paths where the data should be replaced.
     */
    tableColumnReplacementMap: Map<number, Map<string, string[]>>;
    /**
     * Map of table index to ChartData object. Used to handle data delta updates.
     */
    chartDataMap: Map<number, DhType.plot.ChartData>;
    /**
     * Map of table index to object where the keys are column names and the values are arrays of data.
     * This data is the full array of data for the column since ChartData doesn't have a clean way to get it at any time.
     */
    tableDataMap: Map<number, {
        [key: string]: unknown[];
    }>;
    plotlyData: Data[];
    layout: Partial<Layout>;
    isPaused: boolean;
    hasPendingUpdate: boolean;
    hasInitialLoadCompleted: boolean;
    isDownsamplingDisabled: boolean;
    getData(): Partial<Data>[];
    getLayout(): Partial<Layout>;
    close(): void;
    subscribe(callback: (event: CustomEvent) => void): Promise<void>;
    unsubscribe(callback: (event: CustomEvent) => void): void;
    updateLayout(data: PlotlyChartWidgetData): void;
    handleWidgetUpdated(data: PlotlyChartWidgetData, references: DhType.Widget['exportedObjects']): void;
    handleFigureUpdated(event: CustomEvent<DhType.SubscriptionTableData>, tableId: number): void;
    addTable(id: number, table: DhType.Table): Promise<void>;
    updateDownsampledTable(id: number): Promise<void>;
    setDownsamplingDisabled(isDownsamplingDisabled: boolean): void;
    /**
     * Gets info on how to downsample a table for plotting.
     * @param tableId The tableId to get downsample info for
     * @param table The table to get downsample info for
     * @returns DownsampleInfo if table can be downsampled.
     *          A string of the reason if the table cannot be downsampled.
     *          Null if the table does not need downsampling.
     */
    getDownsampleInfo(tableId: number, table: DhType.Table): DownsampleInfo | string;
    subscribeTable(id: number): void;
    removeTable(id: number): void;
    fireUpdate(data: unknown): void;
    setDimensions(rect: DOMRect): void;
    pauseUpdates(): void;
    resumeUpdates(): void;
    shouldPauseOnUserInteraction(): boolean;
    hasScene(): boolean;
    hasGeo(): boolean;
    hasMapbox(): boolean;
    hasPolar(): boolean;
    getPlotWidth(): number;
    getPlotHeight(): number;
}
export default PlotlyExpressChartModel;
//# sourceMappingURL=PlotlyExpressChartModel.d.ts.map