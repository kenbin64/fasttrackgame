/**
 * Dimensional VPS Optimizer - VS Code Extension
 * 
 * Applies Ken's Dimensional Computing paradigm to VPS optimization:
 * - z = x·y multiplicative binding (scale-invariant)
 * - 7-Layer Genesis Model (SPARK → COMPLETION)
 * - Fibonacci alignment [1, 1, 2, 3, 5, 8, 13]
 * - Intention vectors for priority-driven optimization
 * - Lineage graphs for explainability
 * 
 * @author ButterflyFX
 * @version 0.1.0
 */

import * as vscode from 'vscode';
import { exec, spawn, ChildProcess } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// =============================================================================
// CONSTANTS - The 7 Layers (Genesis Model) with Fibonacci Alignment
// =============================================================================

enum Layer {
    SPARK = 1,       // Fibonacci: 1 - Pure potential, input lifting
    MIRROR = 2,      // Fibonacci: 1 - Reflection, manifold mapping
    RELATION = 3,    // Fibonacci: 2 - Connection, multiplicative binding
    FORM = 4,        // Fibonacci: 3 - Structure, navigation
    LIFE = 5,        // Fibonacci: 5 - Dynamics, transformation
    MIND = 6,        // Fibonacci: 8 - Integration, merging
    COMPLETION = 7   // Fibonacci: 13 - Fulfillment, resolution
}

const LAYER_FIBONACCI: Map<Layer, number> = new Map([
    [Layer.SPARK, 1],
    [Layer.MIRROR, 1],
    [Layer.RELATION, 2],
    [Layer.FORM, 3],
    [Layer.LIFE, 5],
    [Layer.MIND, 8],
    [Layer.COMPLETION, 13]
]);

const LAYER_NAMES: Map<Layer, string> = new Map([
    [Layer.SPARK, 'Spark'],
    [Layer.MIRROR, 'Mirror'],
    [Layer.RELATION, 'Relation'],
    [Layer.FORM, 'Form'],
    [Layer.LIFE, 'Life'],
    [Layer.MIND, 'Mind'],
    [Layer.COMPLETION, 'Completion']
]);

const PHI = (1 + Math.sqrt(5)) / 2; // Golden ratio φ ≈ 1.618

// =============================================================================
// INTERFACES - Dimensional Computing Types
// =============================================================================

interface LineageNode {
    id: string;
    operation: string;
    timestamp: number;
    inputIds: string[];
    outputValue: any;
    layer: Layer;
}

interface DimensionalCoordinate {
    spiral: number;    // Which spiral iteration (0-indexed)
    layer: Layer;      // Current layer (1-7)
    position: number;  // Position within layer (0.0 to 1.0)
}

interface DimensionalObject {
    id: string;
    identityVector: [number, number];  // [x, y] where z = x * y
    intentionVector: number[];         // Priority weights
    contextMap: Map<string, any>;
    semanticPayload: any;              // VPS data (CPU, memory, etc.)
    coordinate: DimensionalCoordinate;
    lineageNodes: LineageNode[];
    deltaSet: Set<string>;
}

interface VPSMetrics {
    cpu: {
        usage: number;
        cores: number;
        load: number[];
    };
    memory: {
        total: number;
        used: number;
        free: number;
        percentage: number;
    };
    disk: {
        total: number;
        used: number;
        free: number;
        percentage: number;
    };
    network: {
        bytesIn: number;
        bytesOut: number;
    };
    processes: ProcessInfo[];
    uptime: number;
}

interface ProcessInfo {
    pid: number;
    name: string;
    cpu: number;
    memory: number;
    user: string;
}

// =============================================================================
// DIMENSIONAL KERNEL - The 7 Core Operations
// =============================================================================

class DimensionalKernel {
    private objects: Map<string, DimensionalObject> = new Map();
    private lineageGraph: LineageNode[] = [];
    private substateRules: Map<string, (obj: DimensionalObject) => DimensionalObject> = new Map();

    /**
     * Generate a unique ID for dimensional objects
     */
    private generateId(): string {
        return Math.random().toString(16).substring(2, 14);
    }

    /**
     * LIFT (Layer 1: Spark) - Convert raw data into Dimensional Object
     * Maps input to manifold coordinates using [size, 1/size] for neutral z ≈ 1
     */
    lift(payload: any, intention: number[] = [1, 0, 0]): DimensionalObject {
        const size = this.computePayloadSize(payload);
        const x = Math.max(0.001, size);
        const y = 1 / x;  // Neutral mapping: z = x * (1/x) = 1
        
        const obj: DimensionalObject = {
            id: this.generateId(),
            identityVector: [x, y],
            intentionVector: intention,
            contextMap: new Map([['source', 'VPS'], ['liftedAt', Date.now()]]),
            semanticPayload: payload,
            coordinate: { spiral: 0, layer: Layer.SPARK, position: 0 },
            lineageNodes: [],
            deltaSet: new Set()
        };

        // Record lineage
        const node: LineageNode = {
            id: this.generateId(),
            operation: 'lift',
            timestamp: Date.now(),
            inputIds: [],
            outputValue: obj.id,
            layer: Layer.SPARK
        };
        obj.lineageNodes.push(node);
        this.lineageGraph.push(node);

        this.objects.set(obj.id, obj);
        return obj;
    }

    /**
     * MAP (Layer 2: Mirror) - Update identity vector based on manifold projection
     */
    map(obj: DimensionalObject, transform: (v: [number, number]) => [number, number]): DimensionalObject {
        const newIdentity = transform(obj.identityVector);
        const newObj: DimensionalObject = {
            ...obj,
            identityVector: newIdentity,
            coordinate: { ...obj.coordinate, layer: Layer.MIRROR }
        };

        const node: LineageNode = {
            id: this.generateId(),
            operation: 'map',
            timestamp: Date.now(),
            inputIds: [obj.id],
            outputValue: { oldZ: this.computeZ(obj), newZ: this.computeZ(newObj) },
            layer: Layer.MIRROR
        };
        newObj.lineageNodes.push(node);
        this.lineageGraph.push(node);

        this.objects.set(newObj.id, newObj);
        return newObj;
    }

    /**
     * BIND (Layer 3: Relation) - Multiplicative binding z = x·y (scale-invariant)
     */
    bind(obj1: DimensionalObject, obj2: DimensionalObject): DimensionalObject {
        const newIdentity: [number, number] = [
            obj1.identityVector[0] * obj2.identityVector[0],
            obj1.identityVector[1] * obj2.identityVector[1]
        ];

        // Merge contexts
        const newContext = new Map(obj1.contextMap);
        obj2.contextMap.forEach((v, k) => newContext.set(k, v));

        // Merge intentions (weighted average)
        const newIntention = obj1.intentionVector.map((v, i) => 
            (v + (obj2.intentionVector[i] || 0)) / 2
        );

        const boundObj: DimensionalObject = {
            id: this.generateId(),
            identityVector: newIdentity,
            intentionVector: newIntention,
            contextMap: newContext,
            semanticPayload: { bound: [obj1.semanticPayload, obj2.semanticPayload] },
            coordinate: { spiral: Math.max(obj1.coordinate.spiral, obj2.coordinate.spiral), layer: Layer.RELATION, position: 0 },
            lineageNodes: [...obj1.lineageNodes, ...obj2.lineageNodes],
            deltaSet: new Set([...obj1.deltaSet, ...obj2.deltaSet])
        };

        const node: LineageNode = {
            id: this.generateId(),
            operation: 'bind',
            timestamp: Date.now(),
            inputIds: [obj1.id, obj2.id],
            outputValue: { z: this.computeZ(boundObj) },
            layer: Layer.RELATION
        };
        boundObj.lineageNodes.push(node);
        this.lineageGraph.push(node);

        this.objects.set(boundObj.id, boundObj);
        return boundObj;
    }

    /**
     * NAVIGATE (Layer 4: Form) - Move through dimensional space
     */
    navigate(obj: DimensionalObject, target: Partial<DimensionalCoordinate>): DimensionalObject {
        const newCoord: DimensionalCoordinate = {
            spiral: target.spiral ?? obj.coordinate.spiral,
            layer: target.layer ?? Layer.FORM,
            position: target.position ?? obj.coordinate.position
        };

        const navObj: DimensionalObject = {
            ...obj,
            coordinate: newCoord
        };

        const node: LineageNode = {
            id: this.generateId(),
            operation: 'navigate',
            timestamp: Date.now(),
            inputIds: [obj.id],
            outputValue: { from: obj.coordinate, to: newCoord },
            layer: Layer.FORM
        };
        navObj.lineageNodes.push(node);
        this.lineageGraph.push(node);

        this.objects.set(navObj.id, navObj);
        return navObj;
    }

    /**
     * TRANSFORM (Layer 5: Life) - Apply semantic transformation to payload
     */
    transform<T>(obj: DimensionalObject, fn: (payload: any) => T): DimensionalObject {
        const newPayload = fn(obj.semanticPayload);
        
        // Scale identity based on transformation magnitude
        const scaleFactor = PHI; // Use golden ratio for natural scaling
        const newIdentity: [number, number] = [
            obj.identityVector[0] * scaleFactor,
            obj.identityVector[1] / scaleFactor
        ];

        const transformedObj: DimensionalObject = {
            ...obj,
            identityVector: newIdentity,
            semanticPayload: newPayload,
            coordinate: { ...obj.coordinate, layer: Layer.LIFE }
        };

        transformedObj.deltaSet.add(`transform_${Date.now()}`);

        const node: LineageNode = {
            id: this.generateId(),
            operation: 'transform',
            timestamp: Date.now(),
            inputIds: [obj.id],
            outputValue: { result: typeof newPayload === 'object' ? '[object]' : newPayload },
            layer: Layer.LIFE
        };
        transformedObj.lineageNodes.push(node);
        this.lineageGraph.push(node);

        this.objects.set(transformedObj.id, transformedObj);
        return transformedObj;
    }

    /**
     * MERGE (Layer 6: Mind) - Combine multiple objects into unified whole
     */
    merge(objects: DimensionalObject[]): DimensionalObject {
        if (objects.length === 0) {
            throw new Error('Cannot merge empty array');
        }
        if (objects.length === 1) {
            return objects[0];
        }

        // Recursive binding for associative merge
        let result = objects[0];
        for (let i = 1; i < objects.length; i++) {
            result = this.bind(result, objects[i]);
        }

        // Elevate to MIND layer
        result.coordinate.layer = Layer.MIND;

        const node: LineageNode = {
            id: this.generateId(),
            operation: 'merge',
            timestamp: Date.now(),
            inputIds: objects.map(o => o.id),
            outputValue: { count: objects.length, z: this.computeZ(result) },
            layer: Layer.MIND
        };
        result.lineageNodes.push(node);
        this.lineageGraph.push(node);

        return result;
    }

    /**
     * RESOLVE (Layer 7: Completion) - Extract final result with full lineage
     */
    resolve(obj: DimensionalObject): { result: any; explanation: string; z: number; lineage: LineageNode[] } {
        const z = this.computeZ(obj);
        const fibonacci = LAYER_FIBONACCI.get(Layer.COMPLETION) || 13;

        // Generate explanation from lineage
        const explanation = this.generateExplanation(obj);

        const node: LineageNode = {
            id: this.generateId(),
            operation: 'resolve',
            timestamp: Date.now(),
            inputIds: [obj.id],
            outputValue: { z, fibonacci, explanation: explanation.substring(0, 100) },
            layer: Layer.COMPLETION
        };
        obj.lineageNodes.push(node);
        this.lineageGraph.push(node);

        return {
            result: obj.semanticPayload,
            explanation,
            z,
            lineage: obj.lineageNodes
        };
    }

    /**
     * Compute z = x · y (the multiplicative binding value)
     */
    computeZ(obj: DimensionalObject): number {
        return obj.identityVector[0] * obj.identityVector[1];
    }

    /**
     * Compute payload size for manifold mapping
     */
    private computePayloadSize(payload: any): number {
        if (typeof payload === 'number') return Math.abs(payload);
        if (typeof payload === 'string') return payload.length || 1;
        if (Array.isArray(payload)) return payload.length || 1;
        if (typeof payload === 'object' && payload !== null) {
            return Object.keys(payload).length || 1;
        }
        return 1;
    }

    /**
     * Generate human-readable explanation from lineage
     */
    private generateExplanation(obj: DimensionalObject): string {
        const ops = obj.lineageNodes.map(n => 
            `${n.operation.toUpperCase()} at ${LAYER_NAMES.get(n.layer)}`
        );
        return `Dimensional path: ${ops.join(' → ')} | Final z = ${this.computeZ(obj).toFixed(4)}`;
    }

    /**
     * Get all tracked objects
     */
    getObjects(): DimensionalObject[] {
        return Array.from(this.objects.values());
    }

    /**
     * Get full lineage graph
     */
    getLineageGraph(): LineageNode[] {
        return this.lineageGraph;
    }
}

// =============================================================================
// VPS MONITOR - Collect System Metrics
// =============================================================================

class VPSMonitor {
    private outputChannel: vscode.OutputChannel;
    private kernel: DimensionalKernel;

    constructor(outputChannel: vscode.OutputChannel, kernel: DimensionalKernel) {
        this.outputChannel = outputChannel;
        this.kernel = kernel;
    }

    /**
     * Get comprehensive VPS metrics
     */
    async getMetrics(): Promise<VPSMetrics> {
        const [cpu, memory, disk, network, processes, uptime] = await Promise.all([
            this.getCPUMetrics(),
            this.getMemoryMetrics(),
            this.getDiskMetrics(),
            this.getNetworkMetrics(),
            this.getTopProcesses(),
            this.getUptime()
        ]);

        return { cpu, memory, disk, network, processes, uptime };
    }

    private async getCPUMetrics(): Promise<VPSMetrics['cpu']> {
        try {
            const { stdout: loadAvg } = await execAsync('cat /proc/loadavg');
            const loads = loadAvg.trim().split(' ').slice(0, 3).map(Number);
            
            const { stdout: cpuInfo } = await execAsync('nproc');
            const cores = parseInt(cpuInfo.trim());

            const { stdout: stat } = await execAsync("grep 'cpu ' /proc/stat");
            const parts = stat.trim().split(/\s+/).slice(1).map(Number);
            const idle = parts[3];
            const total = parts.reduce((a, b) => a + b, 0);
            const usage = 100 * (1 - idle / total);

            return { usage, cores, load: loads };
        } catch {
            return { usage: 0, cores: 1, load: [0, 0, 0] };
        }
    }

    private async getMemoryMetrics(): Promise<VPSMetrics['memory']> {
        try {
            const { stdout } = await execAsync('free -b');
            const lines = stdout.trim().split('\n');
            const memLine = lines[1].split(/\s+/);
            const total = parseInt(memLine[1]);
            const used = parseInt(memLine[2]);
            const free = parseInt(memLine[3]);
            const percentage = (used / total) * 100;

            return { total, used, free, percentage };
        } catch {
            return { total: 0, used: 0, free: 0, percentage: 0 };
        }
    }

    private async getDiskMetrics(): Promise<VPSMetrics['disk']> {
        try {
            const { stdout } = await execAsync("df -B1 / | tail -1");
            const parts = stdout.trim().split(/\s+/);
            const total = parseInt(parts[1]);
            const used = parseInt(parts[2]);
            const free = parseInt(parts[3]);
            const percentage = parseInt(parts[4]);

            return { total, used, free, percentage };
        } catch {
            return { total: 0, used: 0, free: 0, percentage: 0 };
        }
    }

    private async getNetworkMetrics(): Promise<VPSMetrics['network']> {
        try {
            const { stdout } = await execAsync("cat /proc/net/dev | grep -E '(eth|ens|enp)' | head -1");
            const parts = stdout.trim().split(/\s+/);
            const bytesIn = parseInt(parts[1]) || 0;
            const bytesOut = parseInt(parts[9]) || 0;

            return { bytesIn, bytesOut };
        } catch {
            return { bytesIn: 0, bytesOut: 0 };
        }
    }

    private async getTopProcesses(): Promise<ProcessInfo[]> {
        try {
            const { stdout } = await execAsync('ps aux --sort=-%cpu | head -6 | tail -5');
            const lines = stdout.trim().split('\n');
            
            return lines.map(line => {
                const parts = line.split(/\s+/);
                return {
                    user: parts[0],
                    pid: parseInt(parts[1]),
                    cpu: parseFloat(parts[2]),
                    memory: parseFloat(parts[3]),
                    name: parts.slice(10).join(' ')
                };
            });
        } catch {
            return [];
        }
    }

    private async getUptime(): Promise<number> {
        try {
            const { stdout } = await execAsync('cat /proc/uptime');
            return parseFloat(stdout.split(' ')[0]);
        } catch {
            return 0;
        }
    }

    /**
     * Lift VPS metrics into dimensional objects
     */
    liftMetrics(metrics: VPSMetrics): DimensionalObject[] {
        const config = vscode.workspace.getConfiguration('dimensionalVPS');
        const priority = config.get<string>('intentionPriority', 'balanced');
        
        // Intention vectors based on priority
        const intentions: Record<string, number[]> = {
            energy: [1, 0.2, 0.3],      // Prioritize energy efficiency
            performance: [0.2, 1, 0.3], // Prioritize performance
            balanced: [0.5, 0.5, 0.5]   // Balanced approach
        };
        const intention = intentions[priority] || intentions.balanced;

        return [
            this.kernel.lift({ type: 'cpu', ...metrics.cpu }, intention),
            this.kernel.lift({ type: 'memory', ...metrics.memory }, intention),
            this.kernel.lift({ type: 'disk', ...metrics.disk }, intention),
            this.kernel.lift({ type: 'network', ...metrics.network }, intention)
        ];
    }
}

// =============================================================================
// DASHBOARD PANEL - WebView for Visualization
// =============================================================================

class DashboardPanel {
    public static currentPanel: DashboardPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];
    private readonly _kernel: DimensionalKernel;
    private readonly _monitor: VPSMonitor;
    private _intervalHandle: NodeJS.Timeout | undefined;

    private constructor(panel: vscode.WebviewPanel, kernel: DimensionalKernel, monitor: VPSMonitor) {
        this._panel = panel;
        this._kernel = kernel;
        this._monitor = monitor;

        this._update();
        this._startAutoRefresh();

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
    }

    public static create(extensionUri: vscode.Uri, kernel: DimensionalKernel, monitor: VPSMonitor) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (DashboardPanel.currentPanel) {
            DashboardPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'dimensionalVPSDashboard',
            'Dimensional VPS Dashboard',
            column || vscode.ViewColumn.One,
            { enableScripts: true }
        );

        DashboardPanel.currentPanel = new DashboardPanel(panel, kernel, monitor);
    }

    private async _update() {
        const metrics = await this._monitor.getMetrics();
        const objects = this._monitor.liftMetrics(metrics);
        const lineage = this._kernel.getLineageGraph();

        this._panel.webview.html = this._getHtml(metrics, objects, lineage);
    }

    private _startAutoRefresh() {
        const config = vscode.workspace.getConfiguration('dimensionalVPS');
        const interval = config.get<number>('refreshInterval', 5000);
        
        this._intervalHandle = setInterval(() => this._update(), interval);
    }

    private _getHtml(metrics: VPSMetrics, objects: DimensionalObject[], lineage: LineageNode[]): string {
        const formatBytes = (bytes: number) => {
            const gb = bytes / (1024 * 1024 * 1024);
            return gb >= 1 ? `${gb.toFixed(2)} GB` : `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
        };

        const formatUptime = (seconds: number) => {
            const days = Math.floor(seconds / 86400);
            const hours = Math.floor((seconds % 86400) / 3600);
            const mins = Math.floor((seconds % 3600) / 60);
            return `${days}d ${hours}h ${mins}m`;
        };

        const zValues = objects.map(o => (o.identityVector[0] * o.identityVector[1]).toFixed(4));

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dimensional VPS Dashboard</title>
    <style>
        :root {
            --bg-primary: #1e1e2e;
            --bg-secondary: #2d2d3f;
            --text-primary: #cdd6f4;
            --text-secondary: #a6adc8;
            --accent-blue: #89b4fa;
            --accent-green: #a6e3a1;
            --accent-yellow: #f9e2af;
            --accent-red: #f38ba8;
            --accent-purple: #cba6f7;
            --golden: #f5c211;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            padding: 20px;
        }
        h1 {
            color: var(--golden);
            margin-bottom: 20px;
            font-size: 24px;
        }
        h2 {
            color: var(--accent-purple);
            font-size: 16px;
            margin-bottom: 12px;
            border-bottom: 1px solid var(--bg-secondary);
            padding-bottom: 8px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .card {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 16px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .metric:last-child { border-bottom: none; }
        .metric-label { color: var(--text-secondary); font-size: 13px; }
        .metric-value { font-weight: 600; font-size: 14px; }
        .metric-value.good { color: var(--accent-green); }
        .metric-value.warn { color: var(--accent-yellow); }
        .metric-value.bad { color: var(--accent-red); }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 6px;
        }
        .progress-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        .layers-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
        }
        .layer {
            text-align: center;
            padding: 12px 8px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            font-size: 11px;
        }
        .layer-num {
            font-size: 20px;
            font-weight: bold;
            color: var(--golden);
        }
        .layer-name { color: var(--text-secondary); margin-top: 4px; }
        .layer-fib { color: var(--accent-blue); font-size: 10px; margin-top: 2px; }
        .z-values {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        .z-badge {
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .lineage-list {
            max-height: 200px;
            overflow-y: auto;
            font-size: 12px;
        }
        .lineage-item {
            padding: 6px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            display: flex;
            justify-content: space-between;
        }
        .lineage-op { color: var(--accent-green); text-transform: uppercase; font-weight: 600; }
        .lineage-layer { color: var(--text-secondary); }
    </style>
</head>
<body>
    <h1>⬡ Dimensional VPS Dashboard</h1>
    
    <h2>The 7 Layers (Genesis Model)</h2>
    <div class="layers-grid" style="margin-bottom: 24px;">
        <div class="layer"><div class="layer-num">1</div><div class="layer-name">Spark</div><div class="layer-fib">F: 1</div></div>
        <div class="layer"><div class="layer-num">2</div><div class="layer-name">Mirror</div><div class="layer-fib">F: 1</div></div>
        <div class="layer"><div class="layer-num">3</div><div class="layer-name">Relation</div><div class="layer-fib">F: 2</div></div>
        <div class="layer"><div class="layer-num">4</div><div class="layer-name">Form</div><div class="layer-fib">F: 3</div></div>
        <div class="layer"><div class="layer-num">5</div><div class="layer-name">Life</div><div class="layer-fib">F: 5</div></div>
        <div class="layer"><div class="layer-num">6</div><div class="layer-name">Mind</div><div class="layer-fib">F: 8</div></div>
        <div class="layer"><div class="layer-num">7</div><div class="layer-name">Completion</div><div class="layer-fib">F: 13</div></div>
    </div>

    <div class="grid">
        <div class="card">
            <h2>CPU</h2>
            <div class="metric">
                <span class="metric-label">Usage</span>
                <span class="metric-value ${metrics.cpu.usage < 50 ? 'good' : metrics.cpu.usage < 80 ? 'warn' : 'bad'}">${metrics.cpu.usage.toFixed(1)}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${metrics.cpu.usage}%; background: ${metrics.cpu.usage < 50 ? 'var(--accent-green)' : metrics.cpu.usage < 80 ? 'var(--accent-yellow)' : 'var(--accent-red)'}"></div>
            </div>
            <div class="metric">
                <span class="metric-label">Cores</span>
                <span class="metric-value">${metrics.cpu.cores}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Load (1/5/15m)</span>
                <span class="metric-value">${metrics.cpu.load.map(l => l.toFixed(2)).join(' / ')}</span>
            </div>
        </div>

        <div class="card">
            <h2>Memory</h2>
            <div class="metric">
                <span class="metric-label">Usage</span>
                <span class="metric-value ${metrics.memory.percentage < 60 ? 'good' : metrics.memory.percentage < 85 ? 'warn' : 'bad'}">${metrics.memory.percentage.toFixed(1)}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${metrics.memory.percentage}%; background: ${metrics.memory.percentage < 60 ? 'var(--accent-green)' : metrics.memory.percentage < 85 ? 'var(--accent-yellow)' : 'var(--accent-red)'}"></div>
            </div>
            <div class="metric">
                <span class="metric-label">Used / Total</span>
                <span class="metric-value">${formatBytes(metrics.memory.used)} / ${formatBytes(metrics.memory.total)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Free</span>
                <span class="metric-value good">${formatBytes(metrics.memory.free)}</span>
            </div>
        </div>

        <div class="card">
            <h2>Disk</h2>
            <div class="metric">
                <span class="metric-label">Usage</span>
                <span class="metric-value ${metrics.disk.percentage < 70 ? 'good' : metrics.disk.percentage < 90 ? 'warn' : 'bad'}">${metrics.disk.percentage}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${metrics.disk.percentage}%; background: ${metrics.disk.percentage < 70 ? 'var(--accent-green)' : metrics.disk.percentage < 90 ? 'var(--accent-yellow)' : 'var(--accent-red)'}"></div>
            </div>
            <div class="metric">
                <span class="metric-label">Used / Total</span>
                <span class="metric-value">${formatBytes(metrics.disk.used)} / ${formatBytes(metrics.disk.total)}</span>
            </div>
        </div>

        <div class="card">
            <h2>Network</h2>
            <div class="metric">
                <span class="metric-label">Bytes In</span>
                <span class="metric-value">${formatBytes(metrics.network.bytesIn)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Bytes Out</span>
                <span class="metric-value">${formatBytes(metrics.network.bytesOut)}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Uptime</span>
                <span class="metric-value good">${formatUptime(metrics.uptime)}</span>
            </div>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <h2>Dimensional Objects (z = x·y)</h2>
            <div class="z-values">
                <div class="z-badge">CPU: z=${zValues[0]}</div>
                <div class="z-badge">MEM: z=${zValues[1]}</div>
                <div class="z-badge">DISK: z=${zValues[2]}</div>
                <div class="z-badge">NET: z=${zValues[3]}</div>
            </div>
            <p style="margin-top: 12px; font-size: 11px; color: var(--text-secondary);">
                φ (Golden Ratio) = ${PHI.toFixed(6)} | Neutral z ≈ 1.0 indicates balanced state
            </p>
        </div>

        <div class="card">
            <h2>Lineage Graph (Last 10)</h2>
            <div class="lineage-list">
                ${lineage.slice(-10).reverse().map(n => `
                    <div class="lineage-item">
                        <span class="lineage-op">${n.operation}</span>
                        <span class="lineage-layer">${LAYER_NAMES.get(n.layer as Layer)}</span>
                    </div>
                `).join('')}
                ${lineage.length === 0 ? '<p style="color: var(--text-secondary); font-size: 12px;">No operations yet</p>' : ''}
            </div>
        </div>
    </div>

    <div class="card">
        <h2>Top Processes</h2>
        <table style="width: 100%; font-size: 12px;">
            <thead>
                <tr style="color: var(--text-secondary); text-align: left;">
                    <th style="padding: 8px 4px;">PID</th>
                    <th style="padding: 8px 4px;">Process</th>
                    <th style="padding: 8px 4px;">CPU %</th>
                    <th style="padding: 8px 4px;">MEM %</th>
                    <th style="padding: 8px 4px;">User</th>
                </tr>
            </thead>
            <tbody>
                ${metrics.processes.map(p => `
                    <tr style="border-top: 1px solid rgba(255,255,255,0.1);">
                        <td style="padding: 8px 4px;">${p.pid}</td>
                        <td style="padding: 8px 4px; max-width: 200px; overflow: hidden; text-overflow: ellipsis;">${p.name.substring(0, 30)}</td>
                        <td style="padding: 8px 4px;" class="${p.cpu < 10 ? 'good' : p.cpu < 50 ? 'warn' : 'bad'}">${p.cpu.toFixed(1)}%</td>
                        <td style="padding: 8px 4px;" class="${p.memory < 5 ? 'good' : p.memory < 20 ? 'warn' : 'bad'}">${p.memory.toFixed(1)}%</td>
                        <td style="padding: 8px 4px;">${p.user}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    </div>

    <script>
        // Auto-refresh indicator
        const vscode = acquireVsCodeApi();
        setInterval(() => {
            document.body.style.opacity = '0.95';
            setTimeout(() => document.body.style.opacity = '1', 100);
        }, 5000);
    </script>
</body>
</html>`;
    }

    public dispose() {
        DashboardPanel.currentPanel = undefined;
        if (this._intervalHandle) {
            clearInterval(this._intervalHandle);
        }
        this._panel.dispose();
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) x.dispose();
        }
    }
}

// =============================================================================
// TREE VIEW PROVIDERS
// =============================================================================

class LayersTreeProvider implements vscode.TreeDataProvider<LayerItem> {
    getTreeItem(element: LayerItem): vscode.TreeItem {
        return element;
    }

    getChildren(): LayerItem[] {
        return [
            new LayerItem('1. Spark', 'LIFT - Convert raw data', 'F: 1'),
            new LayerItem('2. Mirror', 'MAP - Manifold projection', 'F: 1'),
            new LayerItem('3. Relation', 'BIND - Multiplicative z=x·y', 'F: 2'),
            new LayerItem('4. Form', 'NAVIGATE - Dimensional space', 'F: 3'),
            new LayerItem('5. Life', 'TRANSFORM - Semantic change', 'F: 5'),
            new LayerItem('6. Mind', 'MERGE - Unify objects', 'F: 8'),
            new LayerItem('7. Completion', 'RESOLVE - Extract result', 'F: 13')
        ];
    }
}

class LayerItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        private description_: string,
        private fibonacci: string
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.tooltip = `${this.description_} | ${this.fibonacci}`;
        this.description = this.fibonacci;
    }
}

// =============================================================================
// EXTENSION ACTIVATION
// =============================================================================

let outputChannel: vscode.OutputChannel;
let kernel: DimensionalKernel;
let monitor: VPSMonitor;

export function activate(context: vscode.ExtensionContext) {
    outputChannel = vscode.window.createOutputChannel('Dimensional VPS');
    kernel = new DimensionalKernel();
    monitor = new VPSMonitor(outputChannel, kernel);

    outputChannel.appendLine('╔════════════════════════════════════════════╗');
    outputChannel.appendLine('║   Dimensional VPS Optimizer Activated      ║');
    outputChannel.appendLine('║   z = x·y | φ = 1.618... | Layers: 1-7     ║');
    outputChannel.appendLine('╚════════════════════════════════════════════╝');

    // Register tree view
    vscode.window.registerTreeDataProvider('dimensionalVPS.layers', new LayersTreeProvider());

    // Command: Lift VPS Data
    const liftCmd = vscode.commands.registerCommand('dimensionalVPS.liftData', async () => {
        try {
            const metrics = await monitor.getMetrics();
            const objects = monitor.liftMetrics(metrics);
            
            outputChannel.appendLine('\n[LIFT] VPS Data lifted to Dimensional Objects:');
            objects.forEach(obj => {
                const z = obj.identityVector[0] * obj.identityVector[1];
                const type = obj.semanticPayload?.type || 'unknown';
                outputChannel.appendLine(`  • ${type}: z = ${z.toFixed(6)} | Layer: ${LAYER_NAMES.get(obj.coordinate.layer)}`);
            });
            outputChannel.show();

            vscode.window.showInformationMessage(
                `Lifted ${objects.length} VPS metrics to Dimensional Objects`
            );
        } catch (error) {
            vscode.window.showErrorMessage(`Lift failed: ${error}`);
        }
    });

    // Command: Optimize Resources
    const optimizeCmd = vscode.commands.registerCommand('dimensionalVPS.optimize', async () => {
        try {
            const metrics = await monitor.getMetrics();
            const objects = monitor.liftMetrics(metrics);
            
            // Bind CPU and Memory for joint optimization
            const cpuObj = objects[0];
            const memObj = objects[1];
            const bound = kernel.bind(cpuObj, memObj);
            
            // Transform with optimization logic
            const optimized = kernel.transform(bound, (payload) => {
                const analysis = {
                    cpuMemRatio: metrics.cpu.usage / (metrics.memory.percentage || 1),
                    recommendation: '',
                    priority: 0
                };
                
                if (metrics.cpu.usage > 80 && metrics.memory.percentage < 50) {
                    analysis.recommendation = 'CPU-bound: Consider scaling CPU or offloading compute';
                    analysis.priority = 1;
                } else if (metrics.memory.percentage > 80 && metrics.cpu.usage < 50) {
                    analysis.recommendation = 'Memory-bound: Consider freeing memory or adding swap';
                    analysis.priority = 2;
                } else if (metrics.cpu.usage > 80 && metrics.memory.percentage > 80) {
                    analysis.recommendation = 'Resource saturation: Scale up or reduce workload';
                    analysis.priority = 3;
                } else {
                    analysis.recommendation = 'Resources balanced. System healthy.';
                    analysis.priority = 0;
                }
                
                return { ...payload, analysis };
            });
            
            // Resolve to get final result
            const result = kernel.resolve(optimized);
            
            outputChannel.appendLine('\n[OPTIMIZE] Resource Analysis Complete:');
            outputChannel.appendLine(`  z-value: ${result.z.toFixed(6)}`);
            outputChannel.appendLine(`  ${result.explanation}`);
            if (result.result.analysis) {
                outputChannel.appendLine(`  Recommendation: ${result.result.analysis.recommendation}`);
            }
            outputChannel.show();

            vscode.window.showInformationMessage(
                result.result.analysis?.recommendation || 'Optimization complete'
            );
        } catch (error) {
            vscode.window.showErrorMessage(`Optimize failed: ${error}`);
        }
    });

    // Command: Show Dashboard
    const dashboardCmd = vscode.commands.registerCommand('dimensionalVPS.showDashboard', () => {
        DashboardPanel.create(context.extensionUri, kernel, monitor);
    });

    // Command: Bind Processes
    const bindCmd = vscode.commands.registerCommand('dimensionalVPS.bindProcesses', async () => {
        try {
            const metrics = await monitor.getMetrics();
            
            if (metrics.processes.length < 2) {
                vscode.window.showWarningMessage('Need at least 2 processes to bind');
                return;
            }

            const processObjs = metrics.processes.slice(0, 4).map(p => 
                kernel.lift({ type: 'process', ...p }, [p.cpu / 100, p.memory / 100, 0])
            );

            const merged = kernel.merge(processObjs);
            const result = kernel.resolve(merged);

            outputChannel.appendLine('\n[BIND] Process Objects Merged:');
            outputChannel.appendLine(`  Objects merged: ${processObjs.length}`);
            outputChannel.appendLine(`  Combined z: ${result.z.toFixed(6)}`);
            outputChannel.appendLine(`  ${result.explanation}`);
            outputChannel.show();

            vscode.window.showInformationMessage(`Merged ${processObjs.length} process objects, z = ${result.z.toFixed(4)}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Bind failed: ${error}`);
        }
    });

    // Command: Navigate Layers
    const navigateCmd = vscode.commands.registerCommand('dimensionalVPS.navigateLayers', async () => {
        const layers = ['Spark', 'Mirror', 'Relation', 'Form', 'Life', 'Mind', 'Completion'];
        const selected = await vscode.window.showQuickPick(layers, {
            placeHolder: 'Select target layer for navigation'
        });

        if (selected) {
            const layerIndex = layers.indexOf(selected) + 1;
            outputChannel.appendLine(`\n[NAVIGATE] Navigating to Layer ${layerIndex}: ${selected}`);
            outputChannel.appendLine(`  Fibonacci value: ${LAYER_FIBONACCI.get(layerIndex as Layer)}`);
            outputChannel.show();
            vscode.window.showInformationMessage(`Navigated to Layer ${layerIndex}: ${selected}`);
        }
    });

    // Command: Resolve Lineage
    const resolveCmd = vscode.commands.registerCommand('dimensionalVPS.resolveLineage', async () => {
        const lineage = kernel.getLineageGraph();
        
        outputChannel.appendLine('\n[RESOLVE] Full Lineage Graph:');
        outputChannel.appendLine(`  Total operations: ${lineage.length}`);
        lineage.forEach((node, i) => {
            outputChannel.appendLine(`  ${i + 1}. ${node.operation.toUpperCase()} @ ${LAYER_NAMES.get(node.layer)}`);
        });
        outputChannel.show();

        vscode.window.showInformationMessage(`Lineage resolved: ${lineage.length} operations traced`);
    });

    // Command: Start Resource Monitor
    const monitorCmd = vscode.commands.registerCommand('dimensionalVPS.monitorResources', async () => {
        DashboardPanel.create(context.extensionUri, kernel, monitor);
        vscode.window.showInformationMessage('Resource monitor started in dashboard');
    });

    // Register all commands
    context.subscriptions.push(
        liftCmd, optimizeCmd, dashboardCmd, bindCmd, 
        navigateCmd, resolveCmd, monitorCmd, outputChannel
    );

    vscode.window.showInformationMessage('Dimensional VPS Optimizer ready! Use Command Palette to access features.');
}

export function deactivate() {
    if (DashboardPanel.currentPanel) {
        DashboardPanel.currentPanel.dispose();
    }
    outputChannel?.dispose();
}
