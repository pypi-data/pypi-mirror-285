import json

import foursquare.map_sdk as map_sdk


def deep_sort_dict(d):
    if isinstance(d, dict):
        # Sort the dictionary by its keys
        sorted_dict = {k: deep_sort_dict(v) for k, v in sorted(d.items())}
        return sorted_dict
    elif isinstance(d, list):
        # Sort each element in the list
        return [deep_sort_dict(elem) for elem in d]
    else:
        # Return non-dict and non-list values as is
        return d


def dicts_equal(a: dict, b: dict) -> bool:
    return json.dumps(deep_sort_dict(a)) == json.dumps(deep_sort_dict(b))


class TestLayersConverions:
    """
    Testing exhaustiveness and corectness of the layer dataclasses'
    serialization and deserialization functions.
    """

    def test_point_layer_conversion(self):
        for point_layer_json in [
            json.loads(
                """{"id":"point-id","type":"point","config":{"dataId":"some-data-id","columnMode":"points","columns":{"lat":"lat","lng":"lng","altitude":"alt","neighbors":"neigh"},"label":"some-label","color":[1, 2, 3],"isVisible":true,"hidden":true,"legend":{"isIncluded":true},"highlightColor":[4, 5, 6],"textLabel":[{"size": 18,"color":[255, 255, 255],"field":[{"field":{"name":"MONTH","type":"integer"},"format":""}],"offset":[0, 0],"anchor":"start","alignment":"center","background": false,"backgroundColor":[0, 0, 200, 255],"outlineColor":[255, 0, 0, 255],"outlineWidth": 0}, {"size": 18,"color":[255, 255, 255],"field":[{"field":{"name":"I_D","type":"integer"},"format":""}],"offset":[0, 0],"anchor":"start","alignment":"center","background": false,"backgroundColor":[0, 0, 200, 255],"outlineColor":[255, 0, 0, 255],"outlineWidth": 0}],"visConfig":{"radius": 3.14,"fixedRadius":true,"opacity": 0.314,"outline":true,"thickness": 1.23,"strokeColor":[10, 11, 12],"radiusRange":[1, 2],"filled":true,"billboard":true,"allowHover":true,"showNeighborOnHover":true,"showHighlightColor":true,"colorRange":{"name":"color-range","type":"customOrdinal","category":"some-cat","colors":["#111111","#222222","#333333"],"reversed":true,"colorMap":[[1,"#111111"], [2,"#222222"], [3,"#333333"]],"colorLegends":{"#111111":"one","#222222":"two","#333333":"three"}},"strokeColorRange":{"name":"stroke-color-range","type":"customOrdinal","category":"some-cat-stroke","colors":["#111111","#222222","#333333"],"reversed":true,"colorMap":[[1,"#111111"], [2,"#222222"], [3,"#333333"]],"colorLegends":{"#111111":"one","#222222":"two","#333333":"three"}}}},"visualChannels":{"colorField":{"type":"string","name":"field-1"},"colorScale":"customOrdinal","strokeColorField":{"type":"integer","name":"field-3"},"strokeColorScale":"jenks","sizeField":{"type":"string","name":"field-2"},"sizeScale":"sqrt"}}"""
            ),
            json.loads(
                """{"id":"point-id","type":"point","config":{"dataId":"data-id","columnMode":"geojson","columns":{"geojson":"col-geojson"},"visConfig":{}},"visualChannels":{"colorField":{},"strokeColorField":{},"sizeField":{}}}"""
            ),
        ]:
            point_layer = map_sdk.PointLayer.from_json(point_layer_json)
            assert dicts_equal(point_layer.to_json(), point_layer_json)

    def test_arc_layer_conversion(self):
        for arc_layer_json in [
            json.loads(
                """{"type":"arc","id":"arc-id","config":{"dataId":"some-data-id","columnMode":"points","columns":{"lat0":"lat-0","lat1":"lat-1","lng0":"lng-0","lng1":"lng-1"},"color":[1,2,3],"hidden":true,"highlightColor":[4,5,6],"isVisible":true,"label":"some-label","legend":{"isIncluded":true},"visConfig":{"opacity":0.314,"sizeRange":[10,20],"targetColor":[7,8,9],"thickness":1.23,"colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"customOrdinal"}}},"visualChannels":{"colorField":{"name":"field-1","type":"type-1"},"colorScale":"customOrdinal","sizeField":{"name":"field-2","type":"type-2"},"sizeScale":"sqrt"}}"""
            ),
            json.loads(
                """{"type":"arc","id":"arc-id","config":{"dataId":"data-id","columnMode":"neighbors","columns":{"neighbors":"col-nbr","lat":"col-lat","lng":"col-lng"},"visConfig":{}},"visualChannels":{"colorField":{},"sizeField":{}}}"""
            ),
        ]:
            arc_layer = map_sdk.ArcLayer.from_json(arc_layer_json)
            assert dicts_equal(arc_layer.to_json(), arc_layer_json)

    def test_line_layer_conversion(self):
        for line_layer_json in [
            json.loads(
                """{"type":"line","id":"line-id","config":{"dataId":"some-data-id","columnMode":"neighbors","columns":{"lat":"lat","lng":"lng","neighbors":"neigh"},"color":[1,2,3],"hidden":true,"isVisible":true,"label":"some-label","legend":{"isIncluded":true},"visConfig":{"elevationScale":5,"sizeRange":[10,20],"targetColor":[12,13,14],"opacity":0.314,"thickness":1.23,"colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"customOrdinal"}}},"visualChannels":{"colorField":{"name":"field-1","type":"string"},"colorScale":"customOrdinal","sizeField":{"name":"field-2","type":"string"},"sizeScale":"sqrt"}}"""
            ),
            json.loads(
                """{"type":"line","id":"line-id","config":{"dataId":"data-id","columnMode":"points","columns":{"lat0":"col-lat0","lng0":"col-lng0","lat1":"col-lat1","lng1":"col-lng1"},"visConfig":{}},"visualChannels":{"colorField":{},"sizeField":{}}}"""
            ),
        ]:
            line_layer = map_sdk.LineLayer.from_json(line_layer_json)
            assert dicts_equal(line_layer.to_json(), line_layer_json)

    def test_grid_layer_conversion(self):
        for grid_layer_json in [
            json.loads(
                """{"id":"grid-id","type":"grid","config":{"dataId":"some-data-id","columns":{"lat":"col-lat","lng":"col-lng"},"color":[1,2,3],"hidden":true,"isVisible":true,"label":"lbl","legend":{"isIncluded":true},"visConfig":{"colorAggregation":"count","colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"customOrdinal"},"coverage":3,"elevationPercentile":[30,40],"elevationScale":5,"enable3d":false,"enableElevationZoomFactor":false,"fixedHeight":false,"opacity":0.1,"percentile":[10,20,30],"sizeAggregation":"stdev","sizeRange":[50,60],"worldUnitSize":7}},"visualChannels":{"colorField":{"name":"col-field","type":"real"},"colorScale":"quantile","sizeField":{"name":"size-field","type":"real"},"sizeScale":"log"}}"""
            ),
            json.loads(
                """{"id":"grid-id","type":"grid","config":{"dataId":"some-data-id","columns":{"lat":"col-lat","lng":"col-lng"},"visConfig":{}},"visualChannels":{"colorField":{},"sizeField":{}}}"""
            ),
        ]:
            grid_layer = map_sdk.GridLayer.from_json(grid_layer_json)
            assert dicts_equal(grid_layer.to_json(), grid_layer_json)

    def test_hexbin_layer_conversion(self):
        for hexbin_layer_json in [
            json.loads(
                """{"id":"hexbin-id","type":"hexagon","config":{"dataId":"some-data-id","columns":{"lat":"col-lat","lng":"col-lng"},"color":[1,2,3],"hidden":true,"isVisible":true,"label":"lbl","legend":{"isIncluded":true},"visConfig":{"colorAggregation":"count","resolution":7,"colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"customOrdinal"},"coverage":3,"elevationPercentile":[30,40],"elevationScale":5,"enable3d":false,"enableElevationZoomFactor":false,"fixedHeight":false,"opacity":0.1,"percentile":[10,20,30],"sizeAggregation":"stdev","sizeRange":[50,60],"worldUnitSize":7}},"visualChannels":{"colorField":{"name":"col-field","type":"real"},"colorScale":"quantile","sizeField":{"name":"size-field","type":"real"},"sizeScale":"log"}}"""
            ),
            json.loads(
                """{"id":"hexbin-id","type":"hexagon","config":{"dataId":"some-data-id","columns":{"lat":"col-lat","lng":"col-lng"},"visConfig":{}},"visualChannels":{"colorField":{},"sizeField":{}}}"""
            ),
        ]:
            grid_layer = map_sdk.HexbinLayer.from_json(hexbin_layer_json)
            assert dicts_equal(grid_layer.to_json(), hexbin_layer_json)

    def test_polygon_layer_conversion(self):
        for polygon_layer_json in [
            json.loads(
                """{"id":"poly-id","type":"geojson","config":{"dataId":"some-data-id","columnMode":"polygon","columns":{"id":"col-id","lat":"col-lat","lng":"col-lng","sortBy":"col-srt-by","altitude":"col-alt"},"color":[1,2,3],"hidden":false,"highlightColor":[3,4,5],"isVisible":true,"label":"lbl","legend":{"isIncluded":true},"textLabel":[{"size":18,"color":[255,255,255],"field":[{"field":{"name":"MONTH","type":"integer"},"format":""}],"offset":[0,0],"anchor":"start","alignment":"center","background":false,"backgroundColor":[0,0,200,255],"outlineColor":[255,0,0,255],"outlineWidth":0},{"size":18,"color":[255,255,255],"field":[{"field":{"name":"I_D","type":"integer"},"format":""}],"offset":[0,0],"anchor":"start","alignment":"center","background":false,"backgroundColor":[0,0,200,255],"outlineColor":[255,0,0,255],"outlineWidth":0}],"visConfig":{"colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"sequential"},"strokeColorRange":{"name":"color-range-2","colors":["#111112","#222222","#333332"],"category":"some-cat-2","colorLegends":{"#111111":"onetwo","#222222":"twotwo","#333333":"threetwo"},"colorMap":[[1,"#111112"],[2,"#222222"],[3,"#333332"]],"type":"diverging"},"elevationScale":4,"enable3d":true,"filled":true,"fixedHeight":false,"heightRange":[10,20],"opacity":0.1,"strokeOpacity":0.2,"radius":5,"radiusRange":[10,20],"sizeRange":[20,30],"strokeColor":[6,7,8],"stroked":true,"thickness":6,"wireframe":false}},"visualChannels":{"colorField":{"name":"col-field","type":"real"},"colorScale":"quantile","strokeColorField":{"name":"stroke-col-field","type":"real"},"strokeColorScale":"jenks","sizeField":{"name":"size-field","type":"real"},"sizeScale":"linear","radiusField":{"name":"radius-field","type":"real"},"radiusScale":"point","heightField":{"name":"height-field","type":"real"},"heightScale":"sqrt"}}"""
            ),
            json.loads(
                """{"id":"poly-id","type":"geojson","config":{"dataId":"some-data-id","columnMode":"polygon","columns":{"id":"col-id","lat":"col-lat","lng":"col-lng"},"visConfig":{}},"visualChannels":{"colorField":{},"strokeColorField":{},"sizeField":{},"heightField":{},"radiusField":{}}}"""
            ),
        ]:
            polygon_layer = map_sdk.PolygonLayer.from_json(polygon_layer_json)
            assert dicts_equal(polygon_layer.to_json(), polygon_layer_json)

    def test_trip_layer_conversion(self):
        for trip_layer_json in [
            json.loads(
                """{"id":"trip-id","type":"trip","config":{"columnMode":"table","dataId":"some-data-id","columns":{"id":"col-id","lat":"col-lat","lng":"col-lng","timestamp":"col-timestamp","altitude":"col-alt"},"color":[1,2,3],"hidden":false,"isVisible":true,"label":"lbl","legend":{"isIncluded":true},"textLabel":[{"size":18,"color":[255,255,255],"field":[{"field":{"name":"MONTH","type":"integer"},"format":""}],"offset":[0,0],"anchor":"start","alignment":"center","background":false,"backgroundColor":[0,0,200,255],"outlineColor":[255,0,0,255],"outlineWidth":0},{"size":18,"color":[255,255,255],"field":[{"field":{"name":"I_D","type":"integer"},"format":""}],"offset":[0,0],"anchor":"start","alignment":"center","background":false,"backgroundColor":[0,0,200,255],"outlineColor":[255,0,0,255],"outlineWidth":0}],"visConfig":{"adjustPitch":5,"adjustRoll":6,"adjustYaw":7,"billboard":false,"colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"sequential"},"sizeRange":[10,20,30],"fadeTrail":true,"fixedPitch":false,"fixedRoll":false,"fixedYaw":false,"invertPitch":false,"invertRoll":false,"invertYaw":false,"opacity":0.2,"sizeScale":1.5,"thickness":3.1,"trailLength":17,"scenegraph":"scenegrph","scenegraphColor":[9,8,7],"scenegraphColorEnabled":true,"scenegraphEnabled":false,"scenegraphUseTrailColor":false}},"visualChannels":{"colorField":{"name":"col-field","type":"real"},"colorScale":"quantile","sizeField":{"name":"size-field","type":"real"},"sizeScale":"linear","rollField":{"name":"roll-field","type":"real"},"rollScale":"linear","pitchField":{"name":"pitch-field","type":"real"},"pitchScale":"linear","yawField":{"name":"yaw-field","type":"real"},"yawScale":"linear"}}"""
            ),
            json.loads(
                """{"id":"trip-id","type":"trip","config":{"dataId":"some-data-id","columnMode":"table","columns":{"id":"col-id","lat":"col-lat","lng":"col-lng","timestamp":"col-timestamp"},"visConfig":{}},"visualChannels":{"colorField":{},"sizeField":{},"rollField":{},"pitchField":{},"yawField":{}}}"""
            ),
        ]:
            trip_layer = map_sdk.TripLayer.from_json(trip_layer_json)
            assert dicts_equal(trip_layer.to_json(), trip_layer_json)

    def test_icon_layer_conversion(self):
        for icon_layer_json in [
            json.loads(
                """{"type":"icon","id":"icon-id","config":{"dataId":"some-data-id","columns":{"lat":"col-lat","lng":"col-lng","icon":"col-icon","altitude":"col-alt"},"color":[1,2,3],"hidden":false,"highlightColor":[4,5,6],"isVisible":true,"label":"lbl","legend":{"isIncluded":true},"visConfig":{"billboard":false,"colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"sequential"},"fixedRadius":false,"opacity":0.2,"radius":5,"radiusRange":[10,20]}},"visualChannels":{"colorField":{"name":"col-field","type":"real"},"colorScale":"quantile","sizeField":{"name":"size-field","type":"real"},"sizeScale":"linear"}}"""
            ),
            json.loads(
                """{"type":"icon","id":"icon-id","config":{"dataId":"some-data-id","columns":{"lat":"col-lat","lng":"col-lng","icon":"col-icon"},"visConfig":{}},"visualChannels":{"colorField":{},"sizeField":{}}}"""
            ),
        ]:
            icon_layer = map_sdk.IconLayer.from_json(icon_layer_json)
            assert dicts_equal(icon_layer.to_json(), icon_layer_json)

    def test_H3_layer_conversion(self):
        for h3_layer_json in [
            json.loads(
                """{"id":"h3-id","type":"hexagonId","config":{"columns":{"hex_id":"col-hex-id"},"dataId":"some-data-id","color":[1,2,3],"hidden":false,"highlightColor":[5,6,7],"isVisible":true,"label":"h3-label","legend":{"isIncluded":true},"textLabel":[{"size":18,"color":[255,255,255],"field":[{"field":{"name":"MONTH","type":"integer"},"format":""}],"offset":[0,0],"anchor":"start","alignment":"center","background":false,"backgroundColor":[0,0,200,255],"outlineColor":[255,0,0,255],"outlineWidth":0},{"size":18,"color":[255,255,255],"field":[{"field":{"name":"I_D","type":"integer"},"format":""}],"offset":[0,0],"anchor":"start","alignment":"center","background":false,"backgroundColor":[0,0,200,255],"outlineColor":[255,0,0,255],"outlineWidth":0}],"visConfig":{"colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"sequential"},"strokeColorRange":{"name":"stroke-color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one-stroke","#222222":"two-stroke","#333333":"three-stroke"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"sequential"},"coverage":5,"coverageRange":[11,21],"elevationScale":6,"enable3d":false,"enableElevationZoomFactor":false,"filled":true,"fixedHeight":false,"opacity":0.9,"outline":true,"thickness":4,"sizeRange":[10,34],"strokeColor":[11,12,13],"strokeOpacity":0.8}},"visualChannels":{"colorField":{"name":"col-field","type":"real"},"colorScale":"quantile","strokeColorField":{"name":"stroke-col-field","type":"real"},"strokeColorScale":"jenks","sizeField":{"name":"size-field","type":"real"},"sizeScale":"linear","coverageField":{"name":"coverage-field","type":"real"},"coverageScale":"linear"}}"""
            ),
            json.loads(
                """{"id":"h3-id","type":"hexagonId","config":{"dataId":"some-data-id","columns":{"hex_id":"col-hex-id"},"visConfig":{}},"visualChannels":{"colorField":{},"strokeColorField":{},"sizeField":{},"coverageField":{}}}"""
            ),
        ]:
            h3_layer = map_sdk.H3Layer.from_json(h3_layer_json)
            assert dicts_equal(h3_layer.to_json(), h3_layer_json)

    def test_3D_layer_conversion(self):
        for threed_layer_json in [
            json.loads(
                """{"id":"3d-id","type":"3D","config":{"columns":{"lat":"col-lat","lng":"col-lng"},"dataId":"3d-data-id","color":[3,4,5],"hidden":false,"isVisible":true,"label":"3d-label","legend":{"isIncluded":true},"visConfig":{"angleX":5,"angleY":6,"angleZ":7,"colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"sequential"},"opacity":0.91,"scenegraph":"scenegraph-val","scenegraphColor":[32,33,34],"scenegraphColorEnabled":true,"sizeScale":2}},"visualChannels":{"colorField":{"name":"col-field","type":"real"},"colorScale":"quantile","sizeField":{"name":"size-field","type":"real"},"sizeScale":"linear"}}"""
            ),
            json.loads(
                """{"id":"3d-id","type":"3D","config":{"dataId":"3d-data-id","columns":{"lat":"col-lat","lng":"col-lng"},"visConfig":{}},"visualChannels":{"colorField":{},"sizeField":{}}}"""
            ),
        ]:
            threed_layer = map_sdk.ThreeDLayer.from_json(threed_layer_json)
            assert dicts_equal(threed_layer.to_json(), threed_layer_json)

    def test_flow_layer_conversion(self):
        for flow_layer_json in [
            json.loads(
                """{"type":"flow","id":"flow-id","config":{"columnMode":"H3","columns":{"sourceH3":"col-src-h3","targetH3":"col-target-h3","count":"col-cnt","sourceName":"col-src-name","targetName":"col-target-name"},"dataId":"flow-data-id","color":[2,3,4],"hidden":false,"isVisible":true,"label":"flow-label","legend":{"isIncluded":true},"visConfig":{"colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"sequential"},"opacity":0.7,"darkBaseMapEnabled":false,"flowAdaptiveScalesEnabled":true,"flowAnimationEnabled":true,"flowClusteringEnabled":true,"flowFadeAmount":15,"flowFadeEnabled":true,"flowLocationTotalsEnabled":true,"maxTopFlowsDisplayNum":150}}}"""
            ),
            json.loads(
                """{"type":"flow","id":"flow-id","config":{"dataId":"flow-data-id","columnMode":"LAT_LNG","columns":{"lat0":"col-lat0","lng0":"col-lng0","lat1":"col-lat1","lng1":"col-lng1","count":"col-cnt","sourceName":"col-src-name","targetName":"col-target-name"},"visConfig":{}}}"""
            ),
        ]:
            flow_layer = map_sdk.FlowLayer.from_json(flow_layer_json)
            assert dicts_equal(flow_layer.to_json(), flow_layer_json)

    def test_heatmap_layer_conversion(self):
        for heatmap_layer_json in [
            json.loads(
                """{"id":"heatmap-id","type":"heatmap","config":{"dataId":"heatmap-data-id","columns":{"lat":"col-lat","lng":"col-lng"},"visConfig":{}},"visualChannels":{"weightField":{}}}"""
            ),
            json.loads(
                """{"type":"heatmap","id":"heatmap-id","config":{"dataId":"heatmap-data-id","columns":{"lat":"col-lat","lng":"col-lng"},"color":[1,2,3],"hidden":false,"isVisible":true,"label":"heatmap-label","legend":{"isIncluded":true},"visConfig":{"colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"customOrdinal"},"intensity":0.3,"opacity":0.4,"radius":5,"threshold":0.7}},"visualChannels":{"weightField":{"name":"col-weight","type":"real"},"weightScale":"log"}}"""
            ),
        ]:
            heatmap_layer = map_sdk.HeatmapLayer.from_json(heatmap_layer_json)
            assert dicts_equal(heatmap_layer.to_json(), heatmap_layer_json)

    def test_s2_layer_conversion(self):
        for s2_layer_json in [
            json.loads(
                """{"id":"s2-id","type":"s2","config":{"dataId":"s2-data","columns":{"token":"col-token"},"visConfig":{}},"visualChannels":{"colorField":{},"strokeColorField":{},"sizeField":{},"heightField":{}}}"""
            ),
            json.loads(
                """{"type":"s2","id":"s2-id","config":{"dataId":"s2-data","columns":{"token":"col-token"},"color":[3,2,1],"hidden":false,"isVisible":false,"label":"s2-label","legend":{"isIncluded":false},"visConfig":{"elevationScale":3,"enable3d":false,"enableElevationZoomFactor":false,"filled":false,"fixedHeight":false,"heightRange":[10,20],"opacity":0.7,"sizeRange":[100,200],"strokeColor":[9,8,7],"stroked":true,"thickness":12,"wireframe":true,"colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"customOrdinal"},"strokeColorRange":{"name":"stroke-color-range","type":"customOrdinal","category":"some-cat-stroke","colors":["#111111","#222222","#333333"],"reversed":true,"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"colorLegends":{"#111111":"one","#222222":"two","#333333":"three"}}}},"visualChannels":{"colorField":{"name":"col-color","type":"integer"},"colorScale":"ordinal","strokeColorField":{"name":"col-colorStroke","type":"real"},"strokeColorScale":"quantize","heightField":{"name":"col-height","type":"real"},"heightScale":"point","sizeField":{"name":"col-size","type":"real"},"sizeScale":"log"}}"""
            ),
        ]:
            s2_layer = map_sdk.S2Layer.from_json(s2_layer_json)
            assert dicts_equal(s2_layer.to_json(), s2_layer_json)

    def test_cluster_layer_conversion(self):
        for cluster_layer_json in [
            json.loads(
                """{"type":"cluster","config":{"dataId":"cluster-data","columns":{"lat":"col-lat","lng":"col-lng"},"visConfig":{}},"id":"cluster-id","visualChannels":{"colorField":{}}}"""
            ),
            json.loads(
                """{"type":"cluster","id":"cluster-id","config":{"dataId":"cluster-data","columns":{"lat":"col-lat","lng":"col-lng"},"color":[1,2,3],"hidden":false,"isVisible":true,"label":"cluster-label","legend":{"isIncluded":true},"visConfig":{"clusterRadius":100,"colorAggregation":"maximum","opacity":0.2,"radiusRange":[10,20],"colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"customOrdinal"}}},"visualChannels":{"colorField":{"name":"col-color","type":"integer"},"colorScale":"ordinal"}}"""
            ),
        ]:
            cluster_layer = map_sdk.ClusterLayer.from_json(cluster_layer_json)
            assert dicts_equal(cluster_layer.to_json(), cluster_layer_json)

    def test_raster_layer_conversion(self):
        for raster_layer_json in [
            json.loads(
                """{"type":"rasterTile","config":{"dataId":"raster-data","visConfig":{}},"id":"raster-id"}"""
            ),
            json.loads(
                """{"type":"rasterTile","id":"raster-id","config":{"dataId":"raster-id","color":[2,3,4],"hidden":false,"isVisible":true,"label":"raster-label","legend":{"isIncluded":true},"visConfig":{"colormapId":"winter","colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"customOrdinal"},"dynamicColor":true,"enableTerrain":true,"filterEnabled":true,"filterRange":[12,230],"gammaContrastFactor":0.3,"linearRescalingFactor":[2,9],"nonLinearRescaling":true,"mosaicId":"123","opacity":0.5,"saturationValue":4,"singleBandName":"band","sigmoidalBiasFactor":2.3,"preset":"singleBand","sigmoidalContrastFactor":8,"stacSearchProvider":"earth-search","useSTACSearching":true,"startDate":"2023-05-23T00:00:00.000Z","endDate":"2024-05-23T00:00:00.000Z"}}}"""
            ),
        ]:
            raster_layer = map_sdk.RasterLayer.from_json(raster_layer_json)
            assert dicts_equal(raster_layer.to_json(), raster_layer_json)

    def test_vector_layer_conversion(self):
        for vector_layer_json in [
            json.loads(
                """{"type":"vectorTile","config":{"dataId":"vector-data","visConfig":{}},"id":"vector-id","visualChannels":{"colorField":{},"strokeColorField":{},"heightField":{}}}"""
            ),
            json.loads(
                """{"type":"vectorTile","config":{"dataId":"vector-data","visConfig":{"colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"customOrdinal"},"dynamicColor":true,"elevationScale":14,"enable3d":true,"heightRange":[10,20],"opacity":0.2,"radius":7,"radiusByZoom":{"stops":[[1,1],[2,4],[3,9],[4,16],[5,25]]},"strokeColor":[5,0,2],"strokeColorRange":{"name":"stroke-color-range","type":"customOrdinal","category":"some-cat-stroke","colors":["#111111","#222222","#333333"],"reversed":true,"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"colorLegends":{"#111111":"one","#222222":"two","#333333":"three"}},"stroked":true,"strokeOpacity":0.7,"strokeWidth":12,"tileUrl":"vector-tile-url","transition":true},"color":[1,2,3],"hidden":false,"isVisible":true,"label":"vector-label","legend":{"isIncluded":true}},"id":"vector-id","visualChannels":{"colorField":{"name":"col-color","type":"integer"},"colorScale":"ordinal","strokeColorField":{"name":"col-colorStroke","type":"real"},"strokeColorScale":"quantize","heightField":{"name":"col-height","type":"real"},"heightScale":"point"}}"""
            ),
        ]:
            vector_layer = map_sdk.VectorLayer.from_json(vector_layer_json)
            assert dicts_equal(vector_layer.to_json(), vector_layer_json)

    def test_hextile_layer_conversion(self):
        for hextile_layer_json in [
            json.loads(
                """{"type":"hexTile","config":{"dataId":"hextile-data","visConfig":{}},"id":"hextile-id","visualChannels":{"colorField":{},"heightField":{}}}"""
            ),
            json.loads(
                """{"type":"hexTile","config":{"dataId":"hextile-data","visConfig":{"cellPerTileThreshold":4,"colorRange":{"name":"color-range","colors":["#111111","#222222","#333333"],"category":"some-cat","colorLegends":{"#111111":"one","#222222":"two","#333333":"three"},"colorMap":[[1,"#111111"],[2,"#222222"],[3,"#333333"]],"reversed":true,"type":"customOrdinal"},"dynamicColor":true,"elevationScale":7,"enable3d":false,"heightRange":[10,20],"opacity":0.1,"percentileRange":[0.1,0.9],"radius":17,"radiusByZoom":{"stops":[[1,1],[2,4],[3,9],[4,16],[5,25]]},"showOutlines":true,"showPoints":true,"strokeColor":[10,20,30],"strokeOpacity":0.2,"tileQuery":"tile-query","tileUrl":"tile-url","transition":false,"usePercentileRange":false},"color":[1,2,3],"hidden":false,"isVisible":true,"label":"hextile-label","legend":{"isIncluded":false}},"id":"hextile-id","visualChannels":{"colorField":{"name":"col-color","type":"integer"},"colorScale":"ordinal","heightField":{"name":"col-height","type":"real"},"heightScale":"point"}}"""
            ),
        ]:
            hextile_layer = map_sdk.HexTileLayer.from_json(hextile_layer_json)
            assert dicts_equal(hextile_layer.to_json(), hextile_layer_json)

    def test_tile3d_layer_conversion(self):
        for tile3d_layer_json in [
            json.loads(
                """{"type":"tile3d","config":{"dataId":"tile3d-data","visConfig":{}},"id":"tile3d-id"}"""
            ),
            json.loads(
                """{"type":"tile3d","config":{"dataId":"tile3d-data","visConfig":{"opacity":0.2},"color":[1,2,3],"hidden":false,"isVisible":true,"label":"tile3d-label","legend":{"isIncluded":false}},"id":"tile3d-id"}"""
            ),
        ]:
            tile3d_layer = map_sdk.ThreeDTileLayer.from_json(tile3d_layer_json)
            assert dicts_equal(tile3d_layer.to_json(), tile3d_layer_json)

    def test_wms_layer_conversion(self):
        for wms_layer_json in [
            json.loads(
                """{"type":"WMS","config":{"dataId":"wms-data","visConfig":{}},"id":"wms-id"}"""
            ),
            json.loads(
                """{"type":"WMS","config":{"dataId":"wms-data","visConfig":{"opacity":0.2,"serviceLayers":["one","two"]},"color":[1,2,3],"hidden":false,"isVisible":true,"label":"wms-label","legend":{"isIncluded":false}},"id":"wms-id"}"""
            ),
        ]:
            wms_layer = map_sdk.WMSLayer.from_json(wms_layer_json)
            assert dicts_equal(wms_layer.to_json(), wms_layer_json)
