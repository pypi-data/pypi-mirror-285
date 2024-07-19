import{c as He,p as xt,d as je,r as p,j as n,R as j,n as Dn,a as xe,C as Ie,b as q,s as St,e as wt,f as re,g as Se,h as Oe,i as Me,k as ge,l as Mt,m as Tt,o as ee,q as It,t as Dt,u as Et,v as s,w as u,x as Ee,$ as E,L as En,y as Ft,z as Pt,A as _t,B as Nt,D as ln,F as Fe,E as oe,G as Vt,H as Rt,I as Fn,S as Ot,J as Kt,Q as on,K as zt,M as At,N as $t,P as Ke,O as Pn,T as Gt,U as Bt,V as Qt,W as Ut,X as Ht,Y as jt,Z as qt,_ as Zt,a0 as Wt,a1 as qe,a2 as B,a3 as Xt,a4 as Jt,a5 as Yt,a6 as ea,a7 as na}from"./vendor-CUDAPm8e.js";import{u as ta,_ as te,a as Pe,b as ae,c as R,T as $,F as _n,d as Q,I,e as M,f as H,A as aa,g as Nn,h as k,i as F,j as V,k as ra,l as ia,P as la,R as A,m as _e,n as oa,o as sa,L as Ze,p as Z,q as W,r as Ne,s as ca,t as da,E as ua,v as ma,w as pa,x as ga,y as ha,z as fa}from"./vendor-arizeai-Do2HOmcL.js";import{u as ya,T as Vn}from"./pages-bN7juCjh.js";import{V as va}from"./vendor-three-DwGkEfCM.js";import{j as Rn,E as On,l as Kn,a as zn,R as We,n as Xe,p as ba}from"./vendor-codemirror-CrdxOlMs.js";const La=e=>{const t=a=>({...e,markdownDisplayMode:"text",setMarkdownDisplayMode:r=>{a({markdownDisplayMode:r})}});return He()(xt(je(t),{name:"arize-phoenix-preferences"}))},An=p.createContext(null);function ll({children:e,...t}){const a=p.useRef();return a.current||(a.current=La(t)),n(An.Provider,{value:a.current,children:e})}function sn(e,t){const a=j.useContext(An);if(!a)throw new Error("Missing PreferencesContext.Provider in the tree");return Dn(a,e,t)}var z=(e=>(e.primary="primary",e.reference="reference",e.corpus="corpus",e))(z||{});function P(e){throw new Error("Unreachable")}function Je(e){return typeof e=="number"||e===null}function ka(e){return typeof e=="string"||e===null}function ol(e){return Array.isArray(e)?e.every(t=>typeof t=="string"):!1}function Ca(e){return typeof e=="object"&&e!==null}const Ye=p.createContext(null);function Ve(){const e=j.useContext(Ye);if(e===null)throw new Error("useInferences must be used within a InferencesProvider");return e}function sl(e){return n(Ye.Provider,{value:{primaryInferences:e.primaryInferences,referenceInferences:e.referenceInferences,corpusInferences:e.corpusInferences,getInferencesNameByRole:t=>{var a,r;switch(t){case z.primary:return e.primaryInferences.name;case z.reference:return((a=e.referenceInferences)==null?void 0:a.name)??"reference";case z.corpus:return((r=e.corpusInferences)==null?void 0:r.name)??"corpus";default:P()}}},children:e.children})}const $n=function(){var e={defaultValue:null,kind:"LocalArgument",name:"clusters"},t={defaultValue:null,kind:"LocalArgument",name:"dataQualityMetricColumnName"},a={defaultValue:null,kind:"LocalArgument",name:"fetchDataQualityMetric"},r={defaultValue:null,kind:"LocalArgument",name:"fetchPerformanceMetric"},i={defaultValue:null,kind:"LocalArgument",name:"performanceMetric"},l=[{alias:null,args:null,kind:"ScalarField",name:"primaryValue",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"referenceValue",storageKey:null}],o=[{alias:null,args:[{kind:"Variable",name:"clusters",variableName:"clusters"}],concreteType:"Cluster",kind:"LinkedField",name:"clusters",plural:!0,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"eventIds",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"driftRatio",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"primaryToCorpusRatio",storageKey:null},{condition:"fetchDataQualityMetric",kind:"Condition",passingValue:!0,selections:[{alias:null,args:[{fields:[{kind:"Variable",name:"columnName",variableName:"dataQualityMetricColumnName"},{kind:"Literal",name:"metric",value:"mean"}],kind:"ObjectValue",name:"metric"}],concreteType:"DatasetValues",kind:"LinkedField",name:"dataQualityMetric",plural:!1,selections:l,storageKey:null}]},{condition:"fetchPerformanceMetric",kind:"Condition",passingValue:!0,selections:[{alias:null,args:[{fields:[{kind:"Variable",name:"metric",variableName:"performanceMetric"}],kind:"ObjectValue",name:"metric"}],concreteType:"DatasetValues",kind:"LinkedField",name:"performanceMetric",plural:!1,selections:l,storageKey:null}]}],storageKey:null}];return{fragment:{argumentDefinitions:[e,t,a,r,i],kind:"Fragment",metadata:null,name:"pointCloudStore_clusterMetricsQuery",selections:o,type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:[e,a,t,r,i],kind:"Operation",name:"pointCloudStore_clusterMetricsQuery",selections:o},params:{cacheID:"86666967012812887ac0a0149d2d2535",id:null,metadata:{},name:"pointCloudStore_clusterMetricsQuery",operationKind:"query",text:`query pointCloudStore_clusterMetricsQuery(
  $clusters: [ClusterInput!]!
  $fetchDataQualityMetric: Boolean!
  $dataQualityMetricColumnName: String
  $fetchPerformanceMetric: Boolean!
  $performanceMetric: PerformanceMetric!
) {
  clusters(clusters: $clusters) {
    id
    eventIds
    driftRatio
    primaryToCorpusRatio
    dataQualityMetric(metric: {metric: mean, columnName: $dataQualityMetricColumnName}) @include(if: $fetchDataQualityMetric) {
      primaryValue
      referenceValue
    }
    performanceMetric(metric: {metric: $performanceMetric}) @include(if: $fetchPerformanceMetric) {
      primaryValue
      referenceValue
    }
  }
}
`}}}();$n.hash="dbfc8c02ba1ec4f2ba0317b371854d9b";const Gn=function(){var e={defaultValue:null,kind:"LocalArgument",name:"clusterMinSamples"},t={defaultValue:null,kind:"LocalArgument",name:"clusterSelectionEpsilon"},a={defaultValue:null,kind:"LocalArgument",name:"coordinates"},r={defaultValue:null,kind:"LocalArgument",name:"dataQualityMetricColumnName"},i={defaultValue:null,kind:"LocalArgument",name:"eventIds"},l={defaultValue:null,kind:"LocalArgument",name:"fetchDataQualityMetric"},o={defaultValue:null,kind:"LocalArgument",name:"fetchPerformanceMetric"},d={defaultValue:null,kind:"LocalArgument",name:"minClusterSize"},c={defaultValue:null,kind:"LocalArgument",name:"performanceMetric"},m=[{alias:null,args:null,kind:"ScalarField",name:"primaryValue",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"referenceValue",storageKey:null}],h=[{alias:null,args:[{kind:"Variable",name:"clusterMinSamples",variableName:"clusterMinSamples"},{kind:"Variable",name:"clusterSelectionEpsilon",variableName:"clusterSelectionEpsilon"},{kind:"Variable",name:"coordinates3d",variableName:"coordinates"},{kind:"Variable",name:"eventIds",variableName:"eventIds"},{kind:"Variable",name:"minClusterSize",variableName:"minClusterSize"}],concreteType:"Cluster",kind:"LinkedField",name:"hdbscanClustering",plural:!0,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"eventIds",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"driftRatio",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"primaryToCorpusRatio",storageKey:null},{condition:"fetchDataQualityMetric",kind:"Condition",passingValue:!0,selections:[{alias:null,args:[{fields:[{kind:"Variable",name:"columnName",variableName:"dataQualityMetricColumnName"},{kind:"Literal",name:"metric",value:"mean"}],kind:"ObjectValue",name:"metric"}],concreteType:"DatasetValues",kind:"LinkedField",name:"dataQualityMetric",plural:!1,selections:m,storageKey:null}]},{condition:"fetchPerformanceMetric",kind:"Condition",passingValue:!0,selections:[{alias:null,args:[{fields:[{kind:"Variable",name:"metric",variableName:"performanceMetric"}],kind:"ObjectValue",name:"metric"}],concreteType:"DatasetValues",kind:"LinkedField",name:"performanceMetric",plural:!1,selections:m,storageKey:null}]}],storageKey:null}];return{fragment:{argumentDefinitions:[e,t,a,r,i,l,o,d,c],kind:"Fragment",metadata:null,name:"pointCloudStore_clustersQuery",selections:h,type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:[i,a,d,e,t,l,r,o,c],kind:"Operation",name:"pointCloudStore_clustersQuery",selections:h},params:{cacheID:"a1a02d970d255935edfcdd797e4ca80d",id:null,metadata:{},name:"pointCloudStore_clustersQuery",operationKind:"query",text:`query pointCloudStore_clustersQuery(
  $eventIds: [ID!]!
  $coordinates: [InputCoordinate3D!]!
  $minClusterSize: Int!
  $clusterMinSamples: Int!
  $clusterSelectionEpsilon: Float!
  $fetchDataQualityMetric: Boolean!
  $dataQualityMetricColumnName: String
  $fetchPerformanceMetric: Boolean!
  $performanceMetric: PerformanceMetric!
) {
  hdbscanClustering(eventIds: $eventIds, coordinates3d: $coordinates, minClusterSize: $minClusterSize, clusterMinSamples: $clusterMinSamples, clusterSelectionEpsilon: $clusterSelectionEpsilon) {
    id
    eventIds
    driftRatio
    primaryToCorpusRatio
    dataQualityMetric(metric: {metric: mean, columnName: $dataQualityMetricColumnName}) @include(if: $fetchDataQualityMetric) {
      primaryValue
      referenceValue
    }
    performanceMetric(metric: {metric: $performanceMetric}) @include(if: $fetchPerformanceMetric) {
      primaryValue
      referenceValue
    }
  }
}
`}}}();Gn.hash="b26f299a862a3bc4f5487ace49db1d43";const Bn=function(){var e={defaultValue:null,kind:"LocalArgument",name:"corpusEventIds"},t={defaultValue:null,kind:"LocalArgument",name:"primaryEventIds"},a={defaultValue:null,kind:"LocalArgument",name:"referenceEventIds"},r={alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},i={alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},l={alias:null,args:null,kind:"ScalarField",name:"type",storageKey:null},o={alias:null,args:null,kind:"ScalarField",name:"value",storageKey:null},d={alias:null,args:null,concreteType:"EventMetadata",kind:"LinkedField",name:"eventMetadata",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"predictionId",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"predictionLabel",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"predictionScore",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"actualLabel",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"actualScore",storageKey:null}],storageKey:null},c={alias:null,args:null,concreteType:"PromptResponse",kind:"LinkedField",name:"promptAndResponse",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"prompt",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"response",storageKey:null}],storageKey:null},m={alias:null,args:null,kind:"ScalarField",name:"documentText",storageKey:null},h=[r,{alias:null,args:null,concreteType:"DimensionWithValue",kind:"LinkedField",name:"dimensions",plural:!0,selections:[{alias:null,args:null,concreteType:"Dimension",kind:"LinkedField",name:"dimension",plural:!1,selections:[i,l],storageKey:null},o],storageKey:null},d,c,m],g=[{alias:null,args:null,concreteType:"Model",kind:"LinkedField",name:"model",plural:!1,selections:[{alias:null,args:null,concreteType:"Inferences",kind:"LinkedField",name:"primaryInferences",plural:!1,selections:[{alias:null,args:[{kind:"Variable",name:"eventIds",variableName:"primaryEventIds"}],concreteType:"Event",kind:"LinkedField",name:"events",plural:!0,selections:h,storageKey:null}],storageKey:null},{alias:null,args:null,concreteType:"Inferences",kind:"LinkedField",name:"referenceInferences",plural:!1,selections:[{alias:null,args:[{kind:"Variable",name:"eventIds",variableName:"referenceEventIds"}],concreteType:"Event",kind:"LinkedField",name:"events",plural:!0,selections:[r,{alias:null,args:null,concreteType:"DimensionWithValue",kind:"LinkedField",name:"dimensions",plural:!0,selections:[{alias:null,args:null,concreteType:"Dimension",kind:"LinkedField",name:"dimension",plural:!1,selections:[r,i,l],storageKey:null},o],storageKey:null},d,c,m],storageKey:null}],storageKey:null},{alias:null,args:null,concreteType:"Inferences",kind:"LinkedField",name:"corpusInferences",plural:!1,selections:[{alias:null,args:[{kind:"Variable",name:"eventIds",variableName:"corpusEventIds"}],concreteType:"Event",kind:"LinkedField",name:"events",plural:!0,selections:h,storageKey:null}],storageKey:null}],storageKey:null}];return{fragment:{argumentDefinitions:[e,t,a],kind:"Fragment",metadata:null,name:"pointCloudStore_eventsQuery",selections:g,type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:[t,a,e],kind:"Operation",name:"pointCloudStore_eventsQuery",selections:g},params:{cacheID:"388c28f19a685a131b1dfd4bac80cb7c",id:null,metadata:{},name:"pointCloudStore_eventsQuery",operationKind:"query",text:`query pointCloudStore_eventsQuery(
  $primaryEventIds: [ID!]!
  $referenceEventIds: [ID!]!
  $corpusEventIds: [ID!]!
) {
  model {
    primaryInferences {
      events(eventIds: $primaryEventIds) {
        id
        dimensions {
          dimension {
            name
            type
          }
          value
        }
        eventMetadata {
          predictionId
          predictionLabel
          predictionScore
          actualLabel
          actualScore
        }
        promptAndResponse {
          prompt
          response
        }
        documentText
      }
    }
    referenceInferences {
      events(eventIds: $referenceEventIds) {
        id
        dimensions {
          dimension {
            id
            name
            type
          }
          value
        }
        eventMetadata {
          predictionId
          predictionLabel
          predictionScore
          actualLabel
          actualScore
        }
        promptAndResponse {
          prompt
          response
        }
        documentText
      }
    }
    corpusInferences {
      events(eventIds: $corpusEventIds) {
        id
        dimensions {
          dimension {
            name
            type
          }
          value
        }
        eventMetadata {
          predictionId
          predictionLabel
          predictionScore
          actualLabel
          actualScore
        }
        promptAndResponse {
          prompt
          response
        }
        documentText
      }
    }
  }
}
`}}}();Bn.hash="00a957322684d9186fdf16d33a75b931";const Qn=function(){var e={defaultValue:null,kind:"LocalArgument",name:"getDimensionCategories"},t={defaultValue:null,kind:"LocalArgument",name:"getDimensionMinMax"},a={defaultValue:null,kind:"LocalArgument",name:"id"},r=[{kind:"Variable",name:"id",variableName:"id"}],i={alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},l={condition:"getDimensionMinMax",kind:"Condition",passingValue:!0,selections:[{alias:"min",args:[{kind:"Literal",name:"metric",value:"min"}],kind:"ScalarField",name:"dataQualityMetric",storageKey:'dataQualityMetric(metric:"min")'},{alias:"max",args:[{kind:"Literal",name:"metric",value:"max"}],kind:"ScalarField",name:"dataQualityMetric",storageKey:'dataQualityMetric(metric:"max")'}]},o={condition:"getDimensionCategories",kind:"Condition",passingValue:!0,selections:[{alias:null,args:null,kind:"ScalarField",name:"categories",storageKey:null}]};return{fragment:{argumentDefinitions:[e,t,a],kind:"Fragment",metadata:null,name:"pointCloudStore_dimensionMetadataQuery",selections:[{kind:"RequiredField",field:{alias:"dimension",args:r,concreteType:null,kind:"LinkedField",name:"node",plural:!1,selections:[{kind:"InlineFragment",selections:[i,l,o],type:"Dimension",abstractKey:null}],storageKey:null},action:"THROW",path:"dimension"}],type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:[a,t,e],kind:"Operation",name:"pointCloudStore_dimensionMetadataQuery",selections:[{alias:"dimension",args:r,concreteType:null,kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"__typename",storageKey:null},{kind:"TypeDiscriminator",abstractKey:"__isNode"},i,{kind:"InlineFragment",selections:[l,o],type:"Dimension",abstractKey:null}],storageKey:null}]},params:{cacheID:"79c15606d5694bd068270b42ed2fe74c",id:null,metadata:{},name:"pointCloudStore_dimensionMetadataQuery",operationKind:"query",text:`query pointCloudStore_dimensionMetadataQuery(
  $id: GlobalID!
  $getDimensionMinMax: Boolean!
  $getDimensionCategories: Boolean!
) {
  dimension: node(id: $id) {
    __typename
    ... on Dimension {
      id
      min: dataQualityMetric(metric: min) @include(if: $getDimensionMinMax)
      max: dataQualityMetric(metric: max) @include(if: $getDimensionMinMax)
      categories @include(if: $getDimensionCategories)
    }
    __isNode: __typename
    id
  }
}
`}}}();Qn.hash="e8fa488a0d466b5e40fdadc1e5227a57";const xa=30,cn=5,dn=100,Sa=0,un=0,mn=.99,wa=500,pn=300,gn=1e5,Ma=10,hn=1,Ta=2,Ia=1,Da=0;var S=(e=>(e.inferences="inferences",e.correctness="correctness",e.dimension="dimension",e))(S||{}),ce=(e=>(e.list="list",e.gallery="gallery",e))(ce||{}),se=(e=>(e.small="small",e.medium="medium",e.large="large",e))(se||{}),w=(e=>(e.primary="primary",e.reference="reference",e.corpus="corpus",e))(w||{}),D=(e=>(e.correct="correct",e.incorrect="incorrect",e.unknown="unknown",e))(D||{});const Ea=["#05fbff","#cb8afd"],Fa=["#00add0","#4500d9"],U="#a5a5a5",ie=U;function Pa(e){return e.endsWith("/")?e.slice(0,-1):e}const _a=`${window.location.protocol}//${window.location.host}${Pa(window.Config.basename)}`,Na=_a+"/graphql",Va=async(e,t,a)=>{const i=await(await fetch(Na,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:e.text,variables:t})})).json();if(Array.isArray(i.errors))throw new Error(`Error fetching GraphQL query '${e.name}' with variables '${JSON.stringify(t)}': ${JSON.stringify(i.errors)}`);return i},Le=new xe.Environment({network:xe.Network.create(Va),store:new xe.Store(new xe.RecordSource,{gcReleaseBufferSize:10})});function Un(e){return e.includes("PRIMARY")?z.primary:e.includes("CORPUS")?z.corpus:z.reference}function en(e){const t=[],a=[],r=[];return e.forEach(i=>{const l=Un(i);l==z.primary?t.push(i):l==z.corpus?r.push(i):a.push(i)}),{primaryEventIds:t,referenceEventIds:a,corpusEventIds:r}}const De=10,he="unknown",Hn=wt,jn=St,Ra=e=>jn[e],Oa=e=>Hn(e/De);var de=(e=>(e.move="move",e.select="select",e))(de||{}),nn=(e=>(e.default="default",e.highlight="highlight",e))(nn||{});const le=()=>Yn()==="light"?Fa:Ea;function cl(){const e=le();return{coloringStrategy:S.inferences,pointGroupVisibility:{[w.primary]:!0,[w.reference]:!0},pointGroupColors:{[w.primary]:e[0],[w.reference]:e[1],[w.corpus]:U},metric:{type:"drift",metric:"euclideanDistance"}}}function dl(){const e=le();return{coloringStrategy:S.inferences,pointGroupVisibility:{[w.primary]:!0,[w.corpus]:!0},pointGroupColors:{[w.primary]:e[0],[w.corpus]:U},metric:{type:"retrieval",metric:"queryDistance"},clusterSort:{dir:"desc",column:"primaryMetricValue"}}}function ul(){return{coloringStrategy:S.correctness,pointGroupVisibility:{[D.correct]:!0,[D.incorrect]:!0,[D.unknown]:!0},pointGroupColors:{[D.correct]:Ie.Discrete2.LightBlueOrange[0],[D.incorrect]:Ie.Discrete2.LightBlueOrange[1],[D.unknown]:ie},metric:{type:"performance",metric:"accuracyScore"},clusterSort:{dir:"asc",column:"primaryMetricValue"}}}const Ka=e=>{const t={loading:!1,errorMessage:null,points:[],eventIdToDataMap:new Map,clusters:[],clusterSort:{dir:"desc",column:"driftRatio"},pointData:null,selectedEventIds:new Set,hoveredEventId:null,highlightedClusterId:null,selectedClusterId:null,canvasMode:"move",pointSizeScale:1,clusterColorMode:"default",coloringStrategy:S.inferences,inferencesVisibility:{primary:!0,reference:!0,corpus:!0},pointGroupVisibility:{[w.primary]:!0,[w.reference]:!0,[w.corpus]:!0},pointGroupColors:{[w.primary]:le()[0],[w.reference]:le()[1],[w.corpus]:U},eventIdToGroup:{},selectionDisplay:ce.gallery,selectionGridSize:se.large,dimension:null,dimensionMetadata:null,umapParameters:{minDist:Sa,nNeighbors:xa,nSamples:wa},hdbscanParameters:{minClusterSize:Ma,clusterMinSamples:Ia,clusterSelectionEpsilon:Da},clustersLoading:!1,metric:{type:"drift",metric:"euclideanDistance"},selectionSearchText:""},a=(r,i)=>({...t,...e,setInitialData:async({points:l,clusters:o,retrievals:d})=>{const c=i(),m=new Map,h=d.reduce((y,b)=>{const{queryId:C}=b;return y[C]?y[C].push(b):y[C]=[b],y},{});l.forEach(y=>{y={...y,retrievals:h[y.eventId]??[]},m.set(y.eventId,y)});const g=o.map(yn).sort(Ae(c.clusterSort));r({loading:!1,points:l,eventIdToDataMap:m,clusters:g,clustersLoading:!1,selectedEventIds:new Set,selectedClusterId:null,pointData:null,eventIdToGroup:Y({points:l,coloringStrategy:c.coloringStrategy,pointsData:c.pointData??{},dimension:c.dimension||null,dimensionMetadata:c.dimensionMetadata})});const f=await $a(l.map(y=>y.eventId)).catch(()=>r({errorMessage:"Failed to load the point events"}));f&&r({pointData:f,clusters:g,clustersLoading:!1,eventIdToGroup:Y({points:l,coloringStrategy:c.coloringStrategy,pointsData:f??{},dimension:c.dimension||null,dimensionMetadata:c.dimensionMetadata})})},setClusters:l=>{const o=i(),d=l.map(yn).sort(Ae(o.clusterSort));r({clusters:d,clustersLoading:!1,selectedClusterId:null,highlightedClusterId:null})},setClusterSort:l=>{const d=[...i().clusters].sort(Ae(l));r({clusterSort:l,clusters:d})},setSelectedEventIds:l=>r({selectedEventIds:l,selectionSearchText:""}),setHoveredEventId:l=>r({hoveredEventId:l}),setHighlightedClusterId:l=>r({highlightedClusterId:l}),setSelectedClusterId:l=>r({selectedClusterId:l,highlightedClusterId:null}),setPointSizeScale:l=>r({pointSizeScale:l}),setCanvasMode:l=>r({canvasMode:l}),setClusterColorMode:l=>r({clusterColorMode:l}),setColoringStrategy:l=>{const o=i();switch(r({coloringStrategy:l}),l){case S.correctness:r({pointGroupVisibility:{[D.correct]:!0,[D.incorrect]:!0,[D.unknown]:!0},pointGroupColors:{[D.correct]:Ie.Discrete2.LightBlueOrange[0],[D.incorrect]:Ie.Discrete2.LightBlueOrange[1],[D.unknown]:ie},dimension:null,dimensionMetadata:null,eventIdToGroup:Y({points:o.points,coloringStrategy:l,pointsData:o.pointData??{},dimension:o.dimension||null,dimensionMetadata:o.dimensionMetadata})});break;case S.inferences:{r({pointGroupVisibility:{[w.primary]:!0,[w.reference]:!0,[w.corpus]:!0},pointGroupColors:{[w.primary]:le()[0],[w.reference]:le()[1],[w.corpus]:U},dimension:null,dimensionMetadata:null,eventIdToGroup:Y({points:o.points,coloringStrategy:l,pointsData:o.pointData??{},dimension:o.dimension||null,dimensionMetadata:o.dimensionMetadata})});break}case S.dimension:{r({pointGroupVisibility:{unknown:!0},pointGroupColors:{unknown:ie},dimension:null,dimensionMetadata:null,eventIdToGroup:Y({points:o.points,coloringStrategy:l,pointsData:o.pointData??{},dimension:o.dimension||null,dimensionMetadata:o.dimensionMetadata})});break}default:P()}},inferencesVisibility:{primary:!0,reference:!0,corpus:!0},setInferencesVisibility:l=>r({inferencesVisibility:l}),setPointGroupVisibility:l=>r({pointGroupVisibility:l}),selectionDisplay:ce.gallery,setSelectionDisplay:l=>r({selectionDisplay:l}),setSelectionGridSize:l=>r({selectionGridSize:l}),reset:()=>{r({points:[],clusters:[],selectedEventIds:new Set,selectedClusterId:null,eventIdToGroup:{}})},setDimension:async l=>{const o=i();r({dimension:l,dimensionMetadata:null});const d=await Aa(l).catch(()=>r({errorMessage:"Failed to load the dimension metadata"}));if(d){if(r({dimensionMetadata:d}),d.categories&&d.categories.length){const c=d.categories.length,h=c<=jn.length?Ra:g=>Hn(g/c);r({pointGroupVisibility:{...d.categories.reduce((g,f)=>({...g,[f]:!0}),{}),unknown:!0},pointGroupColors:{...d.categories.reduce((g,f,y)=>({...g,[f]:h(y)}),{}),unknown:ie},eventIdToGroup:Y({points:o.points,coloringStrategy:o.coloringStrategy,pointsData:o.pointData??{},dimension:l,dimensionMetadata:d})})}else if(d.interval!==null){const c=qn(d.interval);r({pointGroupVisibility:{...c.reduce((m,h)=>({...m,[h.name]:!0}),{}),unknown:!0},pointGroupColors:{...c.reduce((m,h,g)=>({...m,[h.name]:Oa(g)}),{}),unknown:ie},eventIdToGroup:Y({points:o.points,coloringStrategy:o.coloringStrategy,pointsData:o.pointData??{},dimension:l,dimensionMetadata:d})})}}},setDimensionMetadata:l=>r({dimensionMetadata:l}),setUMAPParameters:l=>r({umapParameters:l}),setHDBSCANParameters:async l=>{const o=i();r({hdbscanParameters:l,clustersLoading:!0});const d=await Ga({metric:o.metric,points:o.points,hdbscanParameters:l});o.setClusters(d)},getHDSCANParameters:()=>i().hdbscanParameters,getMetric:()=>i().metric,setErrorMessage:l=>r({errorMessage:l}),setLoading:l=>r({loading:l}),setMetric:async l=>{const o=i();r({metric:l,clustersLoading:!0});const d=await Ba({metric:l,clusters:o.clusters,hdbscanParameters:o.hdbscanParameters});o.setClusters(d)},setSelectionSearchText:l=>r({selectionSearchText:l})});return He()(je(a))},fn=new Intl.NumberFormat([],{maximumFractionDigits:2});function za({min:e,max:t}){return`${fn.format(e)} - ${fn.format(t)}`}function qn({min:e,max:t}){const r=(t-e)/De,i=[];for(let l=0;l<De;l++){const o=e+l*r,d=e+(l+1)*r;i.push({min:o,max:d,name:za({min:o,max:d})})}return i}function ze({numericGroupIntervals:e,numericValue:t}){let a=he,r=e.findIndex(i=>t>=i.min&&t<i.max);return r=r===-1?De-1:r,a=e[r].name,a}function Y(e){const{points:t,coloringStrategy:a,pointsData:r,dimension:i,dimensionMetadata:l}=e,o={},d=t.map(c=>c.eventId);switch(a){case S.inferences:{const{primaryEventIds:c,referenceEventIds:m,corpusEventIds:h}=en(d);c.forEach(g=>{o[g]=w.primary}),m.forEach(g=>{o[g]=w.reference}),h.forEach(g=>{o[g]=w.corpus});break}case S.correctness:{t.forEach(c=>{let m=D.unknown;const{predictionLabel:h,actualLabel:g}=c.eventMetadata;h!==null&&g!==null&&(m=h===g?D.correct:D.incorrect),o[c.eventId]=m});break}case S.dimension:{let c;l&&(l==null?void 0:l.interval)!==null&&(c=qn(l.interval));const m=(i==null?void 0:i.type)==="prediction"&&(i==null?void 0:i.dataType)==="categorical",h=(i==null?void 0:i.type)==="prediction"&&(i==null?void 0:i.dataType)==="numeric",g=(i==null?void 0:i.type)==="actual"&&(i==null?void 0:i.dataType)==="categorical",f=(i==null?void 0:i.type)==="actual"&&(i==null?void 0:i.dataType)==="numeric";t.forEach(y=>{let b=he;const C=r[y.eventId];if(i!=null&&C!=null)if(m)b=C.eventMetadata.predictionLabel??he;else if(h){if(c==null)throw new Error("Cannot color by prediction score without numeric group intervals");const T=C.eventMetadata.predictionScore;typeof T=="number"&&(b=ze({numericGroupIntervals:c,numericValue:T}))}else if(f){if(c==null)throw new Error("Cannot color by actual score without numeric group intervals");const T=C.eventMetadata.actualScore;typeof T=="number"&&(b=ze({numericGroupIntervals:c,numericValue:T}))}else if(g)b=C.eventMetadata.actualLabel??he;else{const T=C.dimensions.find(_=>_.dimension.name===i.name);if(T!=null&&i.dataType==="categorical")b=T.value??he;else if(T!=null&&i.dataType==="numeric"&&c!=null){const _=typeof(T==null?void 0:T.value)=="string"?parseFloat(T.value):null;typeof _=="number"&&(b=ze({numericGroupIntervals:c,numericValue:_}))}}o[y.eventId]=b});break}default:P()}return o}async function Aa(e){const t=await q.fetchQuery(Le,Qn,{id:e.id,getDimensionMinMax:e.dataType==="numeric",getDimensionCategories:e.dataType==="categorical"}).toPromise(),a=t==null?void 0:t.dimension;if(!e)throw new Error("Dimension not found");let r=null;return typeof(a==null?void 0:a.min)=="number"&&typeof(a==null?void 0:a.max)=="number"&&(r={min:a.min,max:a.max}),{interval:r,categories:(a==null?void 0:a.categories)??null}}async function $a(e){var m,h,g,f,y,b;const{primaryEventIds:t,referenceEventIds:a,corpusEventIds:r}=en([...e]),i=await q.fetchQuery(Le,Bn,{primaryEventIds:t,referenceEventIds:a,corpusEventIds:r}).toPromise(),l=((h=(m=i==null?void 0:i.model)==null?void 0:m.primaryInferences)==null?void 0:h.events)??[],o=((f=(g=i==null?void 0:i.model)==null?void 0:g.referenceInferences)==null?void 0:f.events)??[],d=((b=(y=i==null?void 0:i.model)==null?void 0:y.corpusInferences)==null?void 0:b.events)??[];return[...l,...o,...d].reduce((C,N)=>(C[N.id]=N,C),{})}async function Ga({metric:e,points:t,hdbscanParameters:a}){const r=await q.fetchQuery(Le,Gn,{eventIds:t.map(i=>i.eventId),coordinates:t.map(i=>({x:i.position[0],y:i.position[1],z:i.position[2]})),fetchDataQualityMetric:e.type==="dataQuality",dataQualityMetricColumnName:e.type==="dataQuality"?e.dimension.name:null,fetchPerformanceMetric:e.type==="performance",performanceMetric:e.type==="performance"?e.metric:"accuracyScore",...a},{fetchPolicy:"network-only"}).toPromise();return(r==null?void 0:r.hdbscanClustering)??[]}async function Ba({metric:e,clusters:t,hdbscanParameters:a}){const r=await q.fetchQuery(Le,$n,{clusters:t.map(i=>({id:i.id,eventIds:i.eventIds})),fetchDataQualityMetric:e.type==="dataQuality",dataQualityMetricColumnName:e.type==="dataQuality"?e.dimension.name:null,fetchPerformanceMetric:e.type==="performance",performanceMetric:e.type==="performance"?e.metric:"accuracyScore",...a},{fetchPolicy:"network-only"}).toPromise();return(r==null?void 0:r.clusters)??[]}const Ae=e=>(t,a)=>{const{dir:r,column:i}=e,l=r==="asc",o=t[i],d=a[i];return o==null?1:d==null?-1:o>d?l?1:-1:o<d?l?-1:1:0};function yn(e){let t=e.driftRatio,a=null;return e.dataQualityMetric?(t=e.dataQualityMetric.primaryValue,a=e.dataQualityMetric.referenceValue):e.performanceMetric?(t=e.performanceMetric.primaryValue,a=e.performanceMetric.referenceValue):e.primaryToCorpusRatio!=null&&(t=(e.primaryToCorpusRatio+1)/2*100),{...e,size:e.eventIds.length,primaryMetricValue:t,referenceMetricValue:a}}const tn=p.createContext(null);function ml({children:e,...t}){const a=p.useRef();return a.current||(a.current=Ka(t)),n(tn.Provider,{value:a.current,children:e})}function v(e,t){const a=p.useContext(tn);if(!a)throw new Error("Missing PointCloudContext.Provider in the tree");return Dn(a,e,t)}var K=(e=>(e.last_hour="Last Hour",e.last_day="Last Day",e.last_week="Last Week",e.last_month="Last Month",e.last_3_months="Last 3 Months",e.first_hour="First Hour",e.first_day="First Day",e.first_week="First Week",e.first_month="First Month",e.all="All",e))(K||{});const Zn=p.createContext(null);function Qa(){const e=p.useContext(Zn);if(e===null)throw new Error("useTimeRange must be used within a TimeRangeProvider");return e}function Ua(e,t){return p.useMemo(()=>{switch(e){case"Last Hour":{const r=re(Dt(t.end),{roundingMethod:"ceil"});return{start:Et(r,1),end:r}}case"Last Day":{const r=re(It(t.end),{roundingMethod:"ceil"});return{start:ee(r,1),end:r}}case"Last Week":{const r=re(Se(t.end),{roundingMethod:"ceil"});return{start:ee(r,7),end:r}}case"Last Month":{const r=re(Se(t.end),{roundingMethod:"ceil"});return{start:ee(r,30),end:r}}case"Last 3 Months":{const r=re(Se(t.end),{roundingMethod:"ceil"});return{start:ee(r,90),end:r}}case"First Hour":{const r=Mt(t.start);return{start:r,end:Tt(r,1)}}case"First Day":{const r=ge(t.start);return{start:r,end:Me(r,1)}}case"First Week":{const r=Oe(t.start);return{start:r,end:Me(r,7)}}case"First Month":{const r=Oe(t.start);return{start:r,end:Me(r,30)}}case"All":{const r=re(Se(t.end),{roundingMethod:"floor"});return{start:Oe(t.start),end:r}}default:P()}},[e,t])}function pl(e){const[t,a]=p.useState("Last Month"),r=Ua(t,e.timeRangeBounds),i=p.useCallback(l=>{p.startTransition(()=>{a(l)})},[]);return n(Zn.Provider,{value:{timeRange:r,timePreset:t,setTimePreset:i},children:e.children})}const Wn=p.createContext(null);function gl({children:e}){const[t,a]=ta({style:{zIndex:1e3}}),r=p.useCallback(l=>{t({variant:"danger",...l})},[t]),i=p.useCallback(l=>{t({variant:"success",...l})},[t]);return s(Wn.Provider,{value:{notify:t,notifyError:r,notifySuccess:i},children:[e,a]})}function Xn(){const e=p.useContext(Wn);if(e===null)throw new Error("useGlobalNotification must be used within a NotificationProvider");return e}function hl(){return Xn().notifyError}function fl(){return Xn().notifySuccess}const Jn="arize-phoenix-theme";function Yn(){return localStorage.getItem(Jn)==="light"?"light":"dark"}const an=p.createContext(null);function G(){const e=p.useContext(an);if(e===null)throw new Error("useTheme must be used within a ThemeProvider");return e}function yl(e){const[t,a]=p.useState(Yn()),r=p.useCallback(i=>{localStorage.setItem(Jn,i),a(i)},[]);return n(an.Provider,{value:{theme:t,setTheme:r},children:e.children})}function vl(e){return s("div",{role:"toolbar",css:u`
        padding: var(--px-spacing-sm) var(--px-spacing-lg);
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        gap: var(--px-spacing-med);
        border-bottom: 1px solid var(--ac-global-border-color-dark);
        flex: none;
        min-height: 29px;
        .toolbar__main {
          display: flex;
          flex-direction: row;
          gap: var(--px-spacing-med);
        }
      `,children:[n("div",{"data-testid":"toolbar-main",className:"toolbar__main",children:e.children}),e.extra?n("div",{"data-testid":"toolbar-extra",children:e.extra}):null]})}const Qe=Ee("%x %H:%M %p");Ee("%H:%M %p");function bl(e){const{timeRange:t,timePreset:a,setTimePreset:r}=Qa(),{primaryInferences:{name:i}}=Ve(),l=i.slice(0,10);return n(_n,{color:"designationTurquoise",children:s($,{delay:0,placement:"bottom right",children:[n(te,{children:s(Pe,{label:"primary inferences",defaultSelectedKey:a,"data-testid":"inferences-time-range","aria-label":"Time range for the primary inferences",addonBefore:l,onSelectionChange:o=>{o!==a&&r(o)},children:[n(E,{children:"All"},K.all),n(E,{children:"Last Hour"},K.last_hour),n(E,{children:"Last Day"},K.last_day),n(E,{children:"Last Week"},K.last_week),n(E,{children:"Last Month"},K.last_month),n(E,{children:"Last 3 Months"},K.last_3_months),n(E,{children:"First Hour"},K.first_hour),n(E,{children:"First Day"},K.first_day),n(E,{children:"First Week"},K.first_week),n(E,{children:"First Month"},K.first_month)]})}),n(ae,{children:s("section",{css:u`
              h4 {
                margin-bottom: 0.5rem;
              }
            `,children:[n(R,{level:4,children:"primary inferences time range"}),s("div",{children:["start: ",Qe(t.start)]}),s("div",{children:["end: ",Qe(t.end)]})]})})]})})}const vn=Ee("%x %X");function Ll({timeRange:e}){const{referenceInferences:t}=Ve(),r=((t==null?void 0:t.name)??"reference").slice(0,10);return n("div",{css:u`
        .ac-textfield {
          min-width: 371px;
        }
      `,children:n(_n,{color:"designationPurple",children:s($,{children:[n(te,{children:n(Q,{label:"reference inferences",isReadOnly:!0,"aria-label":"reference inferences time range",value:`${vn(e.start)} - ${vn(e.end)}`,addonBefore:r})}),n(ae,{children:"The static time range of the reference inferences"})]})})})}const et=function(){var e=[{defaultValue:50,kind:"LocalArgument",name:"count"},{defaultValue:null,kind:"LocalArgument",name:"cursor"},{defaultValue:null,kind:"LocalArgument",name:"endTime"},{defaultValue:null,kind:"LocalArgument",name:"startTime"}],t=[{kind:"Variable",name:"after",variableName:"cursor"},{kind:"Variable",name:"first",variableName:"count"}],a={fields:[{kind:"Variable",name:"end",variableName:"endTime"},{kind:"Variable",name:"start",variableName:"startTime"}],kind:"ObjectValue",name:"timeRange"};return{fragment:{argumentDefinitions:e,kind:"Fragment",metadata:null,name:"ModelSchemaTableDimensionsQuery",selections:[{args:[{kind:"Variable",name:"count",variableName:"count"},{kind:"Variable",name:"cursor",variableName:"cursor"},{kind:"Variable",name:"endTime",variableName:"endTime"},{kind:"Variable",name:"startTime",variableName:"startTime"}],kind:"FragmentSpread",name:"ModelSchemaTable_dimensions"}],type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:e,kind:"Operation",name:"ModelSchemaTableDimensionsQuery",selections:[{alias:null,args:null,concreteType:"Model",kind:"LinkedField",name:"model",plural:!1,selections:[{alias:null,args:t,concreteType:"DimensionConnection",kind:"LinkedField",name:"dimensions",plural:!1,selections:[{alias:null,args:null,concreteType:"DimensionEdge",kind:"LinkedField",name:"edges",plural:!0,selections:[{alias:"dimension",args:null,concreteType:"Dimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"type",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"dataType",storageKey:null},{alias:"cardinality",args:[{kind:"Literal",name:"metric",value:"cardinality"},a],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"percentEmpty",args:[{kind:"Literal",name:"metric",value:"percentEmpty"},a],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"min",args:[{kind:"Literal",name:"metric",value:"min"},a],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"mean",args:[{kind:"Literal",name:"metric",value:"mean"},a],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"max",args:[{kind:"Literal",name:"metric",value:"max"},a],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"psi",args:[{kind:"Literal",name:"metric",value:"psi"},a],kind:"ScalarField",name:"driftMetric",storageKey:null}],storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"cursor",storageKey:null},{alias:null,args:null,concreteType:"Dimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"__typename",storageKey:null}],storageKey:null}],storageKey:null},{alias:null,args:null,concreteType:"PageInfo",kind:"LinkedField",name:"pageInfo",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"endCursor",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"hasNextPage",storageKey:null}],storageKey:null}],storageKey:null},{alias:null,args:t,filters:null,handle:"connection",key:"ModelSchemaTable_dimensions",kind:"LinkedHandle",name:"dimensions"}],storageKey:null}]},params:{cacheID:"0f5ec2a75c6234eefab01cbd1181c564",id:null,metadata:{},name:"ModelSchemaTableDimensionsQuery",operationKind:"query",text:`query ModelSchemaTableDimensionsQuery(
  $count: Int = 50
  $cursor: String = null
  $endTime: DateTime!
  $startTime: DateTime!
) {
  ...ModelSchemaTable_dimensions_4sIU9C
}

fragment ModelSchemaTable_dimensions_4sIU9C on Query {
  model {
    dimensions(first: $count, after: $cursor) {
      edges {
        dimension: node {
          id
          name
          type
          dataType
          cardinality: dataQualityMetric(metric: cardinality, timeRange: {start: $startTime, end: $endTime})
          percentEmpty: dataQualityMetric(metric: percentEmpty, timeRange: {start: $startTime, end: $endTime})
          min: dataQualityMetric(metric: min, timeRange: {start: $startTime, end: $endTime})
          mean: dataQualityMetric(metric: mean, timeRange: {start: $startTime, end: $endTime})
          max: dataQualityMetric(metric: max, timeRange: {start: $startTime, end: $endTime})
          psi: driftMetric(metric: psi, timeRange: {start: $startTime, end: $endTime})
        }
        cursor
        node {
          __typename
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
`}}}();et.hash="fb4c57e0ea77548c4e96ceb418e06614";const nt=function(){var e=["model","dimensions"],t={fields:[{kind:"Variable",name:"end",variableName:"endTime"},{kind:"Variable",name:"start",variableName:"startTime"}],kind:"ObjectValue",name:"timeRange"};return{argumentDefinitions:[{defaultValue:50,kind:"LocalArgument",name:"count"},{defaultValue:null,kind:"LocalArgument",name:"cursor"},{defaultValue:null,kind:"LocalArgument",name:"endTime"},{defaultValue:null,kind:"LocalArgument",name:"startTime"}],kind:"Fragment",metadata:{connection:[{count:"count",cursor:"cursor",direction:"forward",path:e}],refetch:{connection:{forward:{count:"count",cursor:"cursor"},backward:null,path:e},fragmentPathInResult:[],operation:et}},name:"ModelSchemaTable_dimensions",selections:[{alias:null,args:null,concreteType:"Model",kind:"LinkedField",name:"model",plural:!1,selections:[{alias:"dimensions",args:null,concreteType:"DimensionConnection",kind:"LinkedField",name:"__ModelSchemaTable_dimensions_connection",plural:!1,selections:[{alias:null,args:null,concreteType:"DimensionEdge",kind:"LinkedField",name:"edges",plural:!0,selections:[{alias:"dimension",args:null,concreteType:"Dimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"type",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"dataType",storageKey:null},{alias:"cardinality",args:[{kind:"Literal",name:"metric",value:"cardinality"},t],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"percentEmpty",args:[{kind:"Literal",name:"metric",value:"percentEmpty"},t],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"min",args:[{kind:"Literal",name:"metric",value:"min"},t],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"mean",args:[{kind:"Literal",name:"metric",value:"mean"},t],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"max",args:[{kind:"Literal",name:"metric",value:"max"},t],kind:"ScalarField",name:"dataQualityMetric",storageKey:null},{alias:"psi",args:[{kind:"Literal",name:"metric",value:"psi"},t],kind:"ScalarField",name:"driftMetric",storageKey:null}],storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"cursor",storageKey:null},{alias:null,args:null,concreteType:"Dimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"__typename",storageKey:null}],storageKey:null}],storageKey:null},{alias:null,args:null,concreteType:"PageInfo",kind:"LinkedField",name:"pageInfo",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"endCursor",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"hasNextPage",storageKey:null}],storageKey:null}],storageKey:null}],storageKey:null}],type:"Query",abstractKey:null}}();nt.hash="fb4c57e0ea77548c4e96ceb418e06614";function tt(e){return n("div",{onClick:t=>t.stopPropagation(),css:u`
        display: inline-block;
      `,children:n(En,{css:u`
          color: var(--ac-global-color-primary);
          &:not(:hover) {
            text-decoration: none;
          }
        `,...e})})}const at=e=>u`
  font-size: ${e.typography.sizes.medium.fontSize}px;
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  thead {
    position: sticky;
    top: 0;
    z-index: 1;
    tr {
      th {
        padding: ${e.spacing.margin4}px ${e.spacing.margin16}px;
        background-color: var(--ac-global-color-grey-100);
        position: relative;
        text-align: left;
        user-select: none;
        border-bottom: 1px solid var(--ac-global-border-color-default);
        &:not(:last-of-type) {
          border-right: 1px solid var(--ac-global-border-color-default);
        }
        .cursor-pointer {
          cursor: pointer;
        }
        .sort-icon {
          margin-left: ${e.spacing.margin4}px;
          font-size: ${e.typography.sizes.small.fontSize}px;
          vertical-align: middle;
          display: inline-block;
        }
        &:hover .resizer {
          background: var(--ac-global-color-grey-300);
        }
        div.resizer {
          display: inline-block;

          width: 2px;
          height: 100%;
          position: absolute;
          right: 0;
          top: 0;
          cursor: grab;
          z-index: 4;
          touch-action: none;
          &.isResizing,
          &:hover {
            background: var(--ac-global-color-primary);
          }
        }
      }
    }
  }
  tbody:not(.is-empty) {
    tr {
      &:not(:last-of-type) {
        & > td {
          border-bottom: 1px solid var(--ac-global-border-color-default);
        }
      }
      &:hover {
        background-color: rgba(var(--ac-global-color-grey-300-rgb), 0.3);
      }
      & > td {
        padding: ${e.spacing.margin8}px ${e.spacing.margin16}px;
      }
    }
  }
`,kl=u`
  tbody:not(.is-empty) {
    tr {
      &:not(:last-of-type) {
        & > td {
          border-bottom: 1px solid var(--ac-global-border-color-default);
        }
      }
      & > td:not(:last-of-type) {
        border-right: 1px solid var(--ac-global-border-color-default);
      }
    }
  }
`,Cl=e=>u(at(e),u`
      tbody:not(.is-empty) {
        tr {
          cursor: pointer;
        }
      }
    `),Ha=e=>u`
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: ${e.spacing.margin8}px;
  gap: ${e.spacing.margin4}px;
  border-top: 1px solid var(--ac-global-color-grey-300);
`;function ja(){return n("tbody",{className:"is-empty",children:n("tr",{children:n("td",{colSpan:100,css:e=>u`
            text-align: center;
            padding: ${e.spacing.margin24}px ${e.spacing.margin24}px !important;
          `,children:"No Data"})})})}function rt({columns:e,data:t}){const a=Ft({columns:e,data:t,getCoreRowModel:Pt(),getPaginationRowModel:_t(),getSortedRowModel:Nt()}),r=a.getRowModel().rows,l=r.length>0?n("tbody",{children:r.map(o=>n("tr",{children:o.getVisibleCells().map(d=>n("td",{children:ln(d.column.columnDef.cell,d.getContext())},d.id))},o.id))}):n(ja,{});return s(Fe,{children:[s("table",{css:at,children:[n("thead",{children:a.getHeaderGroups().map(o=>n("tr",{children:o.headers.map(d=>n("th",{colSpan:d.colSpan,children:d.isPlaceholder?null:n("div",{children:ln(d.column.columnDef.header,d.getContext())})},d.id))},o.id))}),l]}),s("div",{css:Ha,children:[n(H,{variant:"default",size:"compact",onClick:a.previousPage,disabled:!a.getCanPreviousPage(),"aria-label":"Previous Page",icon:n(I,{svg:n(M.ArrowIosBackOutline,{})})}),n(H,{variant:"default",size:"compact",onClick:a.nextPage,disabled:!a.getCanNextPage(),"aria-label":"Next Page",icon:n(I,{svg:n(M.ArrowIosForwardOutline,{})})})]})]})}function it(e){return Math.abs(e)<1e6?oe(",")(e):oe("0.2s")(e)}function ye(e){const t=Math.abs(e);return t===0?"0.00":t<.01?oe(".2e")(e):t<1e3?oe("0.2f")(e):oe("0.2s")(e)}function qa(e){return oe(".2f")(e)+"%"}function Ue(e){return Number.isInteger(e)?it(e):ye(e)}function Re(e){return t=>typeof t!="number"?"--":e(t)}const Za=Re(it),lt=Re(ye),bn=Re(Ue),Wa=Re(qa);function fe({getValue:e}){const t=e();if(!Je(t))throw new Error("IntCell only supports number or null values.");return n("span",{title:t!=null?String(t):"",children:lt(t)})}const Xa=u`
  float: right;
`;function Ja({getValue:e}){const t=e();if(!Je(t))throw new Error("IntCell only supports number or null values.");return n("span",{title:t!=null?String(t):"",css:Xa,children:Za(t)})}function Ya({getValue:e}){const t=e();if(!Je(t))throw new Error("IntCell only supports number or null values.");return n("span",{title:t!=null?String(t):"",children:Wa(t)})}const Ln=100;function er(e){return e.length>Ln?`${e.slice(0,Ln)}...`:e}function xl({getValue:e}){const t=e(),a=t!=null&&typeof t=="string"?er(t):"--";return n("span",{title:String(t),children:a})}function Sl({getValue:e}){const t=e(),a=t!=null&&typeof t=="string"?t:"--";return n("pre",{style:{whiteSpace:"pre-wrap"},children:a})}const nr=u`
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
`;function kn(e,t){return e.length>t?`${e.slice(0,t)}...`:e}function tr({json:e,maxLength:t,space:a=0,disableTitle:r=!1}){const i=typeof t=="number",l=p.useMemo(()=>JSON.stringify(e,null,a),[e,a]),o=p.useMemo(()=>JSON.stringify(e,null,2),[e]),d=r?void 0:o;if(!Ca(e))return console.warn("JSONText component received a non-object value",e),n("span",{title:d,children:String(e)});const c=e;if(Object.keys(c).length===0)return n("span",{title:d,children:"--"});if(Object.keys(c).length===1){const f=Object.keys(c)[0],y=c[f];if(typeof y=="string"){const b=i?kn(y,t):y;return n("span",{title:d,children:b})}}const m=i?kn(l,t):l;return n(i?"span":"pre",{title:d,css:i?void 0:nr,children:m})}const ar=100;function wl({getValue:e}){const t=e();return n(tr,{json:t,maxLength:ar})}function Ml(e){const{data:t}=q.usePaginationFragment(nt,e.model),a=p.useMemo(()=>t.model.dimensions.edges.map(({dimension:i})=>({...i})),[t]),r=j.useMemo(()=>[{header:"name",accessorKey:"name",cell:l=>n(tt,{to:`dimensions/${l.row.original.id}`,children:l.renderValue()})},{header:"type",accessorKey:"type"},{header:"data type",accessorKey:"dataType"},{header:"cardinality",accessorKey:"cardinality",cell:Ja},{header:"% empty",accessorKey:"percentEmpty",cell:Ya},{header:"min",accessorKey:"min",cell:fe},{header:"mean",accessorKey:"mean",cell:fe},{header:"max",accessorKey:"max",cell:fe},{header:"PSI",accessorKey:"psi",cell:fe}],[]);return n(rt,{columns:r,data:a})}const ot=function(){var e=[{defaultValue:50,kind:"LocalArgument",name:"count"},{defaultValue:null,kind:"LocalArgument",name:"cursor"},{defaultValue:null,kind:"LocalArgument",name:"endTime"},{defaultValue:null,kind:"LocalArgument",name:"startTime"}],t=[{kind:"Variable",name:"after",variableName:"cursor"},{kind:"Variable",name:"first",variableName:"count"}];return{fragment:{argumentDefinitions:e,kind:"Fragment",metadata:null,name:"ModelEmbeddingsTableEmbeddingDimensionsQuery",selections:[{args:[{kind:"Variable",name:"count",variableName:"count"},{kind:"Variable",name:"cursor",variableName:"cursor"},{kind:"Variable",name:"endTime",variableName:"endTime"},{kind:"Variable",name:"startTime",variableName:"startTime"}],kind:"FragmentSpread",name:"ModelEmbeddingsTable_embeddingDimensions"}],type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:e,kind:"Operation",name:"ModelEmbeddingsTableEmbeddingDimensionsQuery",selections:[{alias:null,args:null,concreteType:"Model",kind:"LinkedField",name:"model",plural:!1,selections:[{alias:null,args:t,concreteType:"EmbeddingDimensionConnection",kind:"LinkedField",name:"embeddingDimensions",plural:!1,selections:[{alias:null,args:null,concreteType:"EmbeddingDimensionEdge",kind:"LinkedField",name:"edges",plural:!0,selections:[{alias:"embedding",args:null,concreteType:"EmbeddingDimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},{alias:"euclideanDistance",args:[{kind:"Literal",name:"metric",value:"euclideanDistance"},{fields:[{kind:"Variable",name:"end",variableName:"endTime"},{kind:"Variable",name:"start",variableName:"startTime"}],kind:"ObjectValue",name:"timeRange"}],kind:"ScalarField",name:"driftMetric",storageKey:null}],storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"cursor",storageKey:null},{alias:null,args:null,concreteType:"EmbeddingDimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"__typename",storageKey:null}],storageKey:null}],storageKey:null},{alias:null,args:null,concreteType:"PageInfo",kind:"LinkedField",name:"pageInfo",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"endCursor",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"hasNextPage",storageKey:null}],storageKey:null}],storageKey:null},{alias:null,args:t,filters:null,handle:"connection",key:"ModelEmbeddingsTable_embeddingDimensions",kind:"LinkedHandle",name:"embeddingDimensions"}],storageKey:null}]},params:{cacheID:"d0057a41a1d9795383a58de89e72ad76",id:null,metadata:{},name:"ModelEmbeddingsTableEmbeddingDimensionsQuery",operationKind:"query",text:`query ModelEmbeddingsTableEmbeddingDimensionsQuery(
  $count: Int = 50
  $cursor: String = null
  $endTime: DateTime!
  $startTime: DateTime!
) {
  ...ModelEmbeddingsTable_embeddingDimensions_4sIU9C
}

fragment ModelEmbeddingsTable_embeddingDimensions_4sIU9C on Query {
  model {
    embeddingDimensions(first: $count, after: $cursor) {
      edges {
        embedding: node {
          id
          name
          euclideanDistance: driftMetric(metric: euclideanDistance, timeRange: {start: $startTime, end: $endTime})
        }
        cursor
        node {
          __typename
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
`}}}();ot.hash="fb7f125f75d1d33a555c16e198dbcbf8";const st=function(){var e=["model","embeddingDimensions"];return{argumentDefinitions:[{defaultValue:50,kind:"LocalArgument",name:"count"},{defaultValue:null,kind:"LocalArgument",name:"cursor"},{defaultValue:null,kind:"LocalArgument",name:"endTime"},{defaultValue:null,kind:"LocalArgument",name:"startTime"}],kind:"Fragment",metadata:{connection:[{count:"count",cursor:"cursor",direction:"forward",path:e}],refetch:{connection:{forward:{count:"count",cursor:"cursor"},backward:null,path:e},fragmentPathInResult:[],operation:ot}},name:"ModelEmbeddingsTable_embeddingDimensions",selections:[{alias:null,args:null,concreteType:"Model",kind:"LinkedField",name:"model",plural:!1,selections:[{alias:"embeddingDimensions",args:null,concreteType:"EmbeddingDimensionConnection",kind:"LinkedField",name:"__ModelEmbeddingsTable_embeddingDimensions_connection",plural:!1,selections:[{alias:null,args:null,concreteType:"EmbeddingDimensionEdge",kind:"LinkedField",name:"edges",plural:!0,selections:[{alias:"embedding",args:null,concreteType:"EmbeddingDimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},{alias:"euclideanDistance",args:[{kind:"Literal",name:"metric",value:"euclideanDistance"},{fields:[{kind:"Variable",name:"end",variableName:"endTime"},{kind:"Variable",name:"start",variableName:"startTime"}],kind:"ObjectValue",name:"timeRange"}],kind:"ScalarField",name:"driftMetric",storageKey:null}],storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"cursor",storageKey:null},{alias:null,args:null,concreteType:"EmbeddingDimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"__typename",storageKey:null}],storageKey:null}],storageKey:null},{alias:null,args:null,concreteType:"PageInfo",kind:"LinkedField",name:"pageInfo",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"endCursor",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"hasNextPage",storageKey:null}],storageKey:null}],storageKey:null}],storageKey:null}],type:"Query",abstractKey:null}}();st.hash="fb7f125f75d1d33a555c16e198dbcbf8";const rr=u`
  display: inline-flex;
  align-items: center;
  background: none;
  color: var(--ac-global-color-primary);
  border: none;
  padding: 0;
  font: inherit;
  cursor: pointer;
  outline: inherit;
  &:hover {
    text-decoration: underline;
  }
`;function Tl(e){const{children:t,onClick:a}=e;return s("button",{css:rr,onClick:a,children:[t," ",n(I,{svg:n(aa,{})})]})}function ke({href:e,children:t}){return s("a",{href:e,target:"_blank",css:u`
        color: var(--ac-global-color-primary);
        text-decoration: none;
        display: flex;
        flex-direction: row;
        align-items: end;
        gap: var(--px-spacing-sm);
        &:hover {
          text-decoration: underline;
        }
        .ac-icon-wrap {
          font-size: 1em;
        }
      `,rel:"noreferrer",children:[t,n(I,{svg:n(M.ExternalLinkOutline,{})})]})}const Il=()=>n("div",{css:u`
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: rgba(0, 0, 0, 0.2);
      `,children:n(Nn,{isIndeterminate:!0,"aria-label":"loading"})}),ir=({message:e})=>s("div",{css:u`
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        width: 100%;
        height: 100%;
        gap: var(--px-spacing-med);
      `,children:[n(Nn,{isIndeterminate:!0,"aria-label":"loading"}),e!=null?n(k,{children:e}):null]});function Dl(e){const{width:t="size-1250"}=e;return n(V,{width:t,backgroundColor:"light",borderStartWidth:"thin",borderStartColor:"dark",padding:"size-200",flex:"none",children:n(F,{direction:"column",alignItems:"end",justifyContent:"center",height:"100%",children:e.children})})}const lr=2e3;function or({text:e,size:t="compact",disabled:a=!1}){const[r,i]=p.useState(!1),l=p.useCallback(()=>{Vt(e),i(!0),setTimeout(()=>{i(!1)},lr)},[e]);return n("div",{className:"copy-to-clipboard-button",children:s($,{delay:0,offset:5,children:[n(H,{variant:"default",disabled:a,icon:n(I,{svg:r?n(M.Checkmark,{}):n(M.ClipboardCopy,{})}),size:t,onClick:l}),n(ae,{children:"Copy"})]})})}function El(e){const{data:t}=q.usePaginationFragment(st,e.model),a=p.useMemo(()=>t.model.embeddingDimensions.edges.map(({embedding:i})=>({...i})),[t]),r=j.useMemo(()=>[{header:"name",accessorKey:"name",cell:({row:l,renderValue:o})=>n(tt,{to:`embeddings/${l.original.id}`,children:o()})},{header:"euclidean distance",accessorKey:"euclideanDistance",cell:fe}],[]);return n(rt,{columns:r,data:a})}const ct=p.createContext(null),sr=()=>{const e=p.useContext(ct);if(e===null)throw new Error("useTimeSlice must be used within a TimeSliceProvider");return e},Fl=({initialTimestamp:e,children:t})=>{const[a,r]=p.useState(e),i=l=>{p.startTransition(()=>{r(l)})};return n(ct.Provider,{value:{selectedTimestamp:a,setSelectedTimestamp:i},children:t})},Pl=e=>{const t=a=>({...e,columnVisibility:{metadata:!1},evaluationVisibility:{},setColumnVisibility:r=>{a({columnVisibility:r})},setEvaluationVisibility:r=>{a({evaluationVisibility:r})}});return He()(je(t))};function cr(){const e=v(a=>a.setPointSizeScale),t=v(a=>a.pointSizeScale);return s(la,{placement:"bottom left",children:[n(H,{variant:"default",size:"compact",icon:n(I,{svg:n(M.OptionsOutline,{})}),"aria-label":"Display Settings"}),n(ia,{children:n(V,{padding:"size-100",children:n(F,{direction:"column",gap:"size-100",children:n(ra,{label:"Point Scale",minValue:0,maxValue:3,step:.1,value:t,onChange:e})})})})]})}const Cn=u`
  display: flex;
  flex-direction: row;
  gap: var(--px-spacing-sm);
`;function dr(e){return typeof e=="string"&&e in de}function ur(e){return s(_e,{defaultValue:e.mode,variant:"inline-button",size:"compact",onChange:t=>{if(dr(t))e.onChange(t);else throw new Error(`Unknown canvas mode: ${t}`)},children:[n(A,{label:"Move",value:de.move,children:s($,{placement:"top",delay:0,offset:10,children:[n(te,{children:s("div",{css:Cn,children:[n(I,{svg:n(M.MoveFilled,{})})," Move"]})}),n(ae,{children:"Move around the canvas using orbital controls"})]})}),n(A,{label:"Select",value:de.select,children:s($,{placement:"top",delay:0,offset:10,children:[n(te,{children:s("div",{css:Cn,children:[n(I,{svg:n(M.LassoOutline,{})})," Select"]})}),n(ae,{children:"Select points using the lasso tool"})]})})]})}function mr({radius:e}){const t=v(c=>c.eventIdToDataMap),a=v(c=>c.highlightedClusterId),r=v(c=>c.selectedClusterId),i=v(c=>c.clusters),{theme:l}=G(),o=v(c=>c.clusterColorMode),d=p.useMemo(()=>i.map(c=>{const{eventIds:m}=c,h=m.map(g=>{var y;return{position:(y=t.get(g))==null?void 0:y.position}}).filter(g=>g.position!==null);return{...c,data:h}}).filter(c=>c.data.length>0),[i,t]);return n(Fe,{children:d.map((c,m)=>{const h=gr({selected:c.id===r,highlighted:c.id===a,clusterColorMode:o});return n(Rt,{data:c.data,opacity:h,wireframe:!0,pointRadius:e,color:pr({theme:l,clusterColorMode:o,index:m,clusterCount:d.length})},`${c.id}__opacity_${String(h)}`)})})}function pr({theme:e,clusterColorMode:t,index:a,clusterCount:r}){return t===nn.default?e==="dark"?"#999999":"#bbbbbb":Fn(a/r)}function gr({selected:e,highlighted:t,clusterColorMode:a}){return a===nn.highlight?1:e?.7:t?.5:0}const hr=2;function fr({pointRadius:e}){const t=v(m=>m.hoveredEventId),a=v(m=>m.pointSizeScale),r=v(m=>m.eventIdToDataMap),i=v(m=>m.pointGroupColors),l=v(m=>m.eventIdToGroup);if(t==null||r==null)return null;const o=r.get(t),d=l[t],c=i[d];return o==null?null:n(Ot,{position:o.position,args:[e*hr],scale:[a,a,a],children:n("meshMatcapMaterial",{color:c,opacity:.7,transparent:!0})})}const xn=1;function yr(){const e=v(i=>i.hoveredEventId),t=v(i=>i.eventIdToDataMap),a=p.useRef(null);Kt((i,l)=>{a.current&&a.current.children.forEach(o=>o.children[0].material.uniforms.dashOffset.value-=l*5)});const r=p.useMemo(()=>{if(e==null)return[];const i=t.get(e);if(i==null)return[];const l=i.retrievals??[];return(l==null?void 0:l.length)===0?[]:l.map(d=>{const c=t.get(d.documentId);return c==null?null:[i.position,c.position]}).filter(d=>d!=null)},[t,e]);return n("group",{ref:a,children:r.map((i,l)=>s("group",{children:[n(on,{start:i[0],end:i[1],color:16777215,opacity:1,transparent:!0,dashed:!0,dashScale:50,gapSize:20,linewidth:xn}),n(on,{start:i[0],end:i[1],color:16777215,linewidth:xn/2,transparent:!0,opacity:.8})]},l))})}const vr=.5,br=.5,Lr=100,Sn=1.7;function wn(e,t){return typeof t=="function"?t(e):t}function kr({primaryData:e,referenceData:t,corpusData:a,color:r,radius:i}){const l=v(x=>x.inferencesVisibility),o=v(x=>x.coloringStrategy),{theme:d}=G(),c=v(x=>x.setSelectedEventIds),m=v(x=>x.selectedEventIds),h=v(x=>x.setSelectedClusterId),g=v(x=>x.setHoveredEventId),f=v(x=>x.pointSizeScale),y=p.useMemo(()=>zt(g,Lr),[g]),b=p.useMemo(()=>o!==S.inferences?"cube":"sphere",[o]),C=p.useMemo(()=>o!==S.inferences?"octahedron":"sphere",[o]),N=p.useMemo(()=>d==="dark"?At(vr):$t(br),[d]),T=p.useMemo(()=>typeof r=="function"?x=>N(r(x)):N(r),[r,N]),_=p.useCallback(x=>!m.has(x.metaData.id)&&m.size>0?wn(x,T):wn(x,r),[m,r,T]),Ce=l.reference&&t,ue=l.corpus&&a,X=p.useCallback(x=>{p.startTransition(()=>{c(new Set([x.metaData.id])),h(null)})},[h,c]),J=p.useCallback(x=>{x==null||x.metaData==null||y(x.metaData.id)},[y]),me=p.useCallback(()=>{y(null)},[y]);return s(Fe,{children:[l.primary?n(Ke,{data:e,pointProps:{color:_,radius:i,scale:f},onPointClicked:X,onPointHovered:J,onPointerLeave:me}):null,Ce?n(Ke,{data:t,pointProps:{color:_,radius:i,size:i?i*Sn:void 0,scale:f},onPointHovered:J,onPointerLeave:me,pointShape:b,onPointClicked:X}):null,ue?n(Ke,{data:a,pointProps:{color:_,radius:i,size:i?i*Sn:void 0,scale:f},onPointHovered:J,onPointerLeave:me,pointShape:C,onPointClicked:X}):null]})}const Cr=/\.(mp4|mov|webm|ogg)(\?|$)/i,xr=/\.(mp3|wav)(\?|$)/i;function Sr(e){return Cr.test(e)}function wr(e){return xr.test(e)}var ne=(e=>(e.square="square",e.circle="circle",e.diamond="diamond",e))(ne||{});const Mr=()=>n("svg",{width:"12px",height:"12px",viewBox:"0 0 12 12",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:n("rect",{width:"12",height:"12",rx:"1",fill:"currentColor"})}),Tr=()=>n("svg",{width:"12px",height:"12px",viewBox:"0 0 12 12",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:n("circle",{cx:"6",cy:"6",r:"6",fill:"currentColor"})}),Ir=()=>n("svg",{width:"12px",height:"12px",viewBox:"0 0 12 12",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:n("path",{d:"M6 0L12 6L6 12L0 6L6 0Z",fill:"currentColor"})});function dt(e){const{shape:t,color:a}=e,r=p.useMemo(()=>{switch(t){case"square":return n(Mr,{});case"circle":return n(Tr,{});case"diamond":return n(Ir,{});default:P()}},[t]);return n("i",{className:"shape-icon",style:{color:a},css:u`
        display: flex;
        flex-direction: row;
        align-items: center;
      `,"aria-hidden":!0,children:r})}function Dr(e){const{rawData:t,linkToData:a,promptAndResponse:r,documentText:i}=e;return i!=null?"document":r!=null?"prompt_response":a!=null?Sr(a)?"video":wr(a)?"audio":"image":t!=null?"raw":"event_metadata"}function Er(e,t){const{rawData:a}=t;switch(e){case"document":return null;case"prompt_response":return null;case"image":return a!=null?"raw":null;case"video":return a!=null?"raw":null;case"audio":return a!=null?"raw":null;case"raw":return"event_metadata";case"event_metadata":return null;default:P()}}function Fr(e){const{onClick:t,onMouseOver:a,onMouseOut:r,color:i,size:l,inferencesName:o,group:d}=e,c=Dr(e),m=l==="large"?Er(c,e):null;return s("div",{"data-testid":"event-item",role:"button","data-size":l,css:u`
        width: 100%;
        height: 100%;
        box-sizing: border-box;
        border-style: solid;
        border-radius: 4px;
        overflow: hidden;

        display: flex;
        flex-direction: column;
        cursor: pointer;
        overflow: hidden;

        border-width: 1px;
        border-color: ${i};
        border-radius: var(--ac-global-rounding-medium);
        transition: border-color 0.2s ease-in-out;
        transition: transform 0.2s ease-in-out;
        &:hover {
          transform: scale(1.04);
        }
        &[data-size="small"] {
          border-width: 2px;
        }
      `,onClick:t,onMouseOver:a,onMouseOut:r,children:[s("div",{className:"event-item__preview-wrap","data-size":l,css:u`
          display: flex;
          flex-direction: row;
          flex: 1 1 auto;
          overflow: hidden;
          & > *:nth-child(1) {
            flex: 1 1 auto;
            overflow: hidden;
          }
          & > *:nth-child(2) {
            flex: none;
            width: 43%;
          }
          &[data-size="large"] {
            & > *:nth-child(1) {
              margin: var(--px-spacing-med);
              border-radius: 8px;
            }
          }
        `,children:[n(Mn,{previewType:c,...e}),m!=null&&n(Mn,{previewType:m,...e})]}),l!=="small"&&n(zr,{color:i,group:d,inferencesName:o,showInferences:l==="large"})]})}function Mn(e){const{previewType:t}=e;let a=null;switch(t){case"document":{a=n(Rr,{...e});break}case"prompt_response":{a=n(Vr,{...e});break}case"image":{a=n(Pr,{...e});break}case"video":{a=n(_r,{...e});break}case"audio":{a=n(Nr,{...e});break}case"raw":{a=n(Or,{...e});break}case"event_metadata":{a=n(Kr,{...e});break}default:P()}return a}function Pr(e){return n("img",{src:e.linkToData||"[error] unexpected missing url",css:u`
        min-height: 0;
        // Maintain aspect ratio while having normalized height
        object-fit: contain;
        transition: background-color 0.2s ease-in-out;
        background-color: ${Pn(.85,e.color)};
      `})}function _r(e){return n("video",{src:e.linkToData||"[error] unexpected missing url",css:u`
        min-height: 0;
        // Maintain aspect ratio while having normalized height
        object-fit: contain;
        transition: background-color 0.2s ease-in-out;
        background-color: ${Pn(.85,e.color)};
      `})}function Nr(e){return n("audio",{src:e.linkToData||"[error] unexpected missing url",autoPlay:e.autoPlay,controls:!0})}function Vr(e){var t,a;return s("div",{"data-size":e.size,css:u`
        --prompt-response-preview-background-color: var(
          --ac-global-color-grey-200
        );
        background-color: var(--prompt-response-preview-background-color);
        &[data-size="small"] {
          display: flex;
          flex-direction: column;
          padding: var(--px-spacing-sm);
          font-size: var(--px-font-size-sm);
          section {
            flex: 1 1 0;
            overflow: hidden;
            header {
              display: none;
            }
          }
        }
        &[data-size="medium"] {
          display: flex;
          flex-direction: column;
          gap: var(--px-spacing-sm);
          padding: var(--px-spacing-med);
          section {
            flex: 1 1 0;
            overflow: hidden;
          }
        }
        &[data-size="large"] {
          display: flex;
          flex-direction: row;
          section {
            padding: var(--px-spacing-sm);
            flex: 1 1 0;
          }
        }
        & > section {
          position: relative;

          header {
            font-weight: bold;
            margin-bottom: var(--px-spacing-sm);
          }
          &:before {
            content: "";
            width: 100%;
            height: 100%;
            position: absolute;
            left: 0;
            top: 0;
            background: linear-gradient(
              transparent 80%,
              var(--prompt-response-preview-background-color) 100%
            );
          }
        }
      `,children:[s("section",{children:[n("header",{children:"prompt"}),(t=e.promptAndResponse)==null?void 0:t.prompt]}),s("section",{children:[n("header",{children:"response"}),(a=e.promptAndResponse)==null?void 0:a.response]})]})}function Rr(e){return n("p",{"data-size":e.size,css:u`
        flex: 1 1 auto;
        padding: var(--px-spacing-med);
        margin-block-start: 0;
        margin-block-end: 0;
        position: relative;
        --text-preview-background-color: var(--ac-global-color-grey-100);
        background-color: var(--text-preview-background-color);

        &[data-size="small"] {
          padding: var(--px-spacing-sm);
          box-sizing: border-box;
        }
        &:before {
          content: "";
          width: 100%;
          height: 100%;
          position: absolute;
          left: 0;
          top: 0;
          background: linear-gradient(
            transparent 90%,
            var(--text-preview-background-color) 98%,
            var(--text-preview-background-color) 100%
          );
        }
      `,children:e.documentText})}function Or(e){return n("p",{"data-size":e.size,css:u`
        flex: 1 1 auto;
        padding: var(--px-spacing-med);
        margin-block-start: 0;
        margin-block-end: 0;
        position: relative;
        --text-preview-background-color: var(--ac-background-color-light);
        background-color: var(--text-preview-background-color);

        &[data-size="small"] {
          padding: var(--px-spacing-sm);
          font-size: var(--ac-global-color-gray-600);
          box-sizing: border-box;
        }
        &:before {
          content: "";
          width: 100%;
          height: 100%;
          position: absolute;
          left: 0;
          top: 0;
          background: linear-gradient(
            transparent 90%,
            var(--text-preview-background-color) 98%,
            var(--text-preview-background-color) 100%
          );
        }
      `,children:e.rawData})}function Kr(e){return s("dl",{css:u`
        margin: 0;
        padding: var(--px-spacing-lg);
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: var(--px-spacing-med);

        dt {
          font-weight: bold;
        }
        dd {
          margin-inline-start: var(--px-spacing-med);
        }
      `,children:[s("div",{children:[n("dt",{children:"prediction label"}),n("dd",{children:e.predictionLabel||"--"})]}),s("div",{children:[n("dt",{children:"actual label"}),n("dd",{children:e.actualLabel||"--"})]})]})}function zr({color:e,group:t,showInferences:a,inferencesName:r}){return s("footer",{css:u`
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        padding: var(--px-spacing-sm) var(--px-spacing-med) var(--px-spacing-sm)
          7px;
        border-top: 1px solid var(--ac-global-border-color-dark);
      `,children:[s("div",{css:u`
          display: flex;
          flex-direction: row;
          align-items: center;
          gap: var(--px-spacing-sm);
        `,children:[n(dt,{shape:ne.circle,color:e}),t]}),a?n("div",{title:"the inferences the point belongs to",children:r}):null]})}const pe=200,we=10,Ar=new va,$r=()=>{const{getInferencesNameByRole:e}=Ve(),t=v(f=>f.hoveredEventId),a=v(f=>f.eventIdToDataMap),r=v(f=>f.pointData),i=v(f=>f.pointGroupColors),l=v(f=>f.eventIdToGroup);if(t==null||r==null||r==null)return null;const o=a.get(t),d=r[t];if(o==null||d==null)return null;const c=l[t],m=i[l[t]],h=Un(t),g=e(h);return n(Gt,{position:o.position,pointerEvents:"none",zIndexRange:[0,1],calculatePosition:(f,y,b)=>{const C=Ar.setFromMatrixPosition(f.matrixWorld);C.project(y);const N=b.width/2,T=b.height/2;return[Math.min(b.width-pe-we,Math.max(0,C.x*N+N+we)),Math.min(b.height-pe-we,Math.max(0,-(C.y*T)+T+we))]},children:n("div",{css:u`
          --grid-item-min-width: ${pe}px;
          width: ${pe}px;
          height: ${pe}px;
          background-color: var(--ac-global-background-color-dark);
          border-radius: var(--ac-global-rounding-medium);
        `,children:n(Fr,{rawData:o.embeddingMetadata.rawData,linkToData:o.embeddingMetadata.linkToData,predictionLabel:o.eventMetadata.predictionLabel,actualLabel:o.eventMetadata.actualLabel,promptAndResponse:d.promptAndResponse,documentText:d.documentText,inferencesName:g,group:c,color:m,size:"medium",autoPlay:!0})})})},Gr=300,Br=3,Qr=.2,Ur=function(){const{selectedTimestamp:t}=sr(),a=v(c=>c.points),r=v(c=>c.hdbscanParameters),i=v(c=>c.umapParameters),[l,o,d]=p.useMemo(()=>{const{primaryEventIds:c,referenceEventIds:m,corpusEventIds:h}=en(a.map(g=>g.eventId));return[c.length,m.length,h.length]},[a]);return t?s("section",{css:u`
        width: 300px;
        padding: var(--px-spacing-med);
      `,children:[s("dl",{css:$e,children:[s("div",{children:[n("dt",{children:"Timestamp"}),n("dd",{children:Qe(t)})]}),s("div",{children:[n("dt",{children:"primary points"}),n("dd",{children:l})]}),o>0?s("div",{children:[n("dt",{children:"reference points"}),n("dd",{children:o})]}):null,d>0?s("div",{children:[n("dt",{children:"corpus points"}),n("dd",{children:d})]}):null]}),n("br",{}),n(R,{level:4,weight:"heavy",children:"Clustering Parameters"}),s("dl",{css:$e,children:[s("div",{children:[n("dt",{children:"min cluster size"}),n("dd",{children:r.minClusterSize})]}),s("div",{children:[n("dt",{children:"cluster min samples"}),n("dd",{children:r.clusterMinSamples})]}),s("div",{children:[n("dt",{children:"cluster selection epsilon"}),n("dd",{children:r.clusterSelectionEpsilon})]})]}),n("br",{}),n(R,{level:4,weight:"heavy",children:"UMAP Parameters"}),s("dl",{css:$e,children:[s("div",{children:[n("dt",{children:"min distance"}),n("dd",{children:i.minDist})]}),s("div",{children:[n("dt",{children:"n neighbors"}),n("dd",{children:i.nNeighbors})]}),s("div",{children:[n("dt",{children:"n samples per inferences"}),n("dd",{children:i.nSamples})]})]})]}):null},$e=u`
  margin: 0;
  padding: 0;
  div {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: var(--px-spacing-sm);
  }
`;function Hr(){const e=v(a=>a.canvasMode),t=v(a=>a.setCanvasMode);return s("div",{css:u`
        position: absolute;
        left: var(--px-spacing-med);
        top: var(--px-spacing-med);
        z-index: 1;
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: var(--px-spacing-med);
      `,children:[n(ur,{mode:e,onChange:t}),n(cr,{}),n(jr,{})]})}function jr(){return s($,{placement:"bottom left",delay:0,children:[n(H,{variant:"default",size:"compact",icon:n(I,{svg:n(oa,{})}),"aria-label":"Information bout the point-cloud display"}),n(sa,{title:"Point Cloud Summary",children:n(Ur,{})})]})}function qr({children:e}){const{theme:t}=G();return n("div",{css:u`
        flex: 1 1 auto;
        height: 100%;
        position: relative;
        &[data-theme="dark"] {
          background: linear-gradient(
            rgb(21, 25, 31) 11.4%,
            rgb(11, 12, 14) 70.2%
          );
        }
        &[data-theme="light"] {
          background: linear-gradient(#f2f6fd 0%, #dbe6fc 74%);
        }
      `,"data-theme":t,children:e})}function _l(){return s(qr,{children:[n(Hr,{},"canvas-tools"),n(Zr,{},"projection")]})}const Zr=j.memo(function(){const t=v(L=>L.points),a=v(L=>L.canvasMode),r=v(L=>L.setSelectedEventIds),i=v(L=>L.setSelectedClusterId),l=v(L=>L.pointGroupColors),o=v(L=>L.pointGroupVisibility),{theme:d}=G(),c=v(L=>L.inferencesVisibility),[m,h]=p.useState(!0),g=p.useMemo(()=>Bt(t.map(L=>L.position)),[t]),f=(g.maxX-g.minX+(g.maxY-g.minY))/2/Gr,y=f*Br,b=a===de.move,C=v(L=>L.eventIdToGroup),N=p.useCallback(L=>{const O=C[L.metaData.id]||"unknown";return l[O]||ie},[l,C]),T=p.useMemo(()=>t.filter(L=>L.eventId.includes("PRIMARY")),[t]),_=p.useMemo(()=>t.filter(L=>L.eventId.includes("REFERENCE")),[t]),Ce=p.useMemo(()=>t.filter(L=>L.eventId.includes("CORPUS")),[t]),ue=p.useMemo(()=>T.filter(L=>{const O=C[L.eventId];return o[O]}),[T,C,o]),X=p.useMemo(()=>!_||_.length===0?null:_.filter(L=>{const O=C[L.eventId];return o[O]}),[_,C,o]),J=p.useMemo(()=>Ce.filter(L=>{const O=C[L.eventId];return o[O]}),[Ce,C,o]),me=p.useMemo(()=>{const L=c.primary?ue:[],O=c.reference?X:[],Ct=c.corpus?J:[];return[...L,...O||[],...Ct||[]]},[ue,X,J,c]),x=Qt(tn,Ye,Wt,an);return n(Zt,{camera:{position:[3,3,3]},children:s(x,{children:[n(Ut,{autoRotate:m,autoRotateSpeed:2,enableRotate:b,enablePan:b,onEnd:()=>{h(!1)}}),s(Ht,{bounds:g,boundsZoomPaddingFactor:Qr,children:[n(jt,{points:me,onChange:L=>{r(new Set(L.map(O=>O.metaData.id))),i(null)},enabled:a===de.select}),n(qt,{size:(g.maxX-g.minX)/4,color:d=="dark"?"#fff":"#505050"}),n(kr,{primaryData:ue,referenceData:X,corpusData:J,color:N,radius:f}),n(mr,{radius:y}),n($r,{}),n(fr,{pointRadius:f}),n(yr,{})]})]})})}),ut=function(){var e=[{alias:null,args:null,concreteType:"Model",kind:"LinkedField",name:"model",plural:!1,selections:[{alias:null,args:null,concreteType:"DimensionConnection",kind:"LinkedField",name:"dimensions",plural:!1,selections:[{alias:null,args:null,concreteType:"DimensionEdge",kind:"LinkedField",name:"edges",plural:!0,selections:[{alias:null,args:null,concreteType:"Dimension",kind:"LinkedField",name:"node",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"type",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"dataType",storageKey:null}],storageKey:null}],storageKey:null}],storageKey:null}],storageKey:null}];return{fragment:{argumentDefinitions:[],kind:"Fragment",metadata:null,name:"DimensionPickerQuery",selections:e,type:"Query",abstractKey:null},kind:"Request",operation:{argumentDefinitions:[],kind:"Operation",name:"DimensionPickerQuery",selections:e},params:{cacheID:"56e356d226d322dabfd9db8010884e4f",id:null,metadata:{},name:"DimensionPickerQuery",operationKind:"query",text:`query DimensionPickerQuery {
  model {
    dimensions {
      edges {
        node {
          id
          name
          type
          dataType
        }
      }
    }
  }
}
`}}}();ut.hash="747256fac1de97803ae6f96e3cb58d98";function Wr(e){const{type:t}=e;let a="gray",r="";switch(t){case"feature":a="blue",r="FEA";break;case"tag":a="purple",r="TAG";break;case"prediction":a="white",r="PRE";break;case"actual":a="orange",r="ACT";break;default:P()}return n(Ze,{color:a,"aria-label":t,title:"type",children:r})}const Xr=s(W,{children:[n(R,{weight:"heavy",level:4,children:"Model Dimension"}),n(Z,{children:n(k,{children:"A dimension is a feature, tag, prediction, or actual value that is associated with a model inference. Features represent inputs, tags represent metadata, predictions represent outputs, and actuals represent ground truth."})})]});function Jr(e){const{selectedDimension:t,dimensions:a,onChange:r,isLoading:i,...l}=e;return n(Pe,{...l,defaultSelectedKey:t?t.name:void 0,"aria-label":"Select a dimension",onSelectionChange:o=>{const d=a.find(c=>c.name===o);d&&p.startTransition(()=>r(d))},label:"Dimension",labelExtra:Xr,isDisabled:i,placeholder:i?"Loading...":"Select a dimension...",children:a.map(o=>n(E,{textValue:o.name,children:s("div",{css:u`
              .ac-label {
                margin-right: var(--px-spacing-med);
              }
            `,children:[n(Wr,{type:o.type}),o.name]})},o.name))})}function Yr(e){const[t,a]=p.useState([]),[r,i]=p.useState(!0),{selectedDimension:l,onChange:o,...d}=e;return p.useEffect(()=>{q.fetchQuery(Le,ut,{},{fetchPolicy:"store-or-network"}).toPromise().then(c=>{const m=(c==null?void 0:c.model.dimensions.edges.map(h=>h.node))??[];a(m),i(!1)})},[]),n(Jr,{...d,onChange:o,dimensions:t,label:"Dimension",selectedDimension:l,isLoading:r})}function ei(e){return typeof e=="string"&&e in S}const ni=Object.values(S),ti=s(W,{children:[n(R,{weight:"heavy",level:4,children:"Coloring Strategy"}),n(Z,{children:n(k,{children:"The way in which inference point is colored. Each point in the point-cloud represents a model inference. These inferences can be colored by a particular attribute (such as inferences and dimension) or by a performance value such as correctness (predicted value equals the actual value)"})})]});function ai(e){const{strategy:t,onChange:a}=e;return n(Pe,{defaultSelectedKey:t,"aria-label":"Coloring strategy",onSelectionChange:r=>{ei(r)&&a(r)},label:"Color By",labelExtra:ti,children:ni.map(r=>n(E,{children:r},r))})}const ri=u`
  display: flex;
  flex-direction: row;
  gap: var(--px-flex-gap-sm);
  align-items: center;
`;function Te(e){const{name:t,checked:a,onChange:r,color:i,iconShape:l=ne.circle}=e;return s("label",{css:ri,children:[n("input",{type:"checkbox",checked:a,name:t,onChange:r}),n(dt,{shape:l,color:i}),t]},t)}function ii({hasReference:e,hasCorpus:t}){const a=v(f=>f.inferencesVisibility),r=v(f=>f.setInferencesVisibility),i=v(f=>f.coloringStrategy),l=p.useCallback(f=>{const{name:y,checked:b}=f.target;r({...a,[y]:b})},[a,r]),o=ya(),d=p.useMemo(()=>{switch(i){case S.inferences:return o[0];case S.correctness:case S.dimension:return U;default:P()}},[i,o]),c=p.useMemo(()=>{switch(i){case S.inferences:return o[1];case S.correctness:case S.dimension:return U;default:P()}},[i,o]),m=U,h=i===S.inferences?ne.circle:ne.square,g=i===S.inferences?ne.circle:ne.diamond;return s("form",{css:u`
        display: flex;
        flex-direction: column;
        padding: var(--px-spacing-med);
      `,children:[n(Te,{checked:a.primary,name:"primary",color:d,onChange:l}),e?n(Te,{checked:a.reference,name:"reference",onChange:l,color:c,iconShape:h}):null,t?n(Te,{checked:a.corpus,name:"corpus",onChange:l,color:m,iconShape:g}):null]})}function li(){const e=v(l=>l.pointGroupVisibility),t=v(l=>l.setPointGroupVisibility),a=v(l=>l.pointGroupColors),r=p.useMemo(()=>Object.keys(e),[e]),i=p.useCallback(l=>{const{name:o,checked:d}=l.target;t({...e,[o]:d})},[e,t]);return s("form",{css:u`
        display: flex;
        flex-direction: column;
      `,children:[n(oi,{}),n("div",{css:u`
          padding: var(--px-spacing-med);
        `,children:r.map(l=>{const o=e[l],d=a[l];return n(Te,{name:l,checked:o,color:d,onChange:i},l)})})]})}function oi(){const e=v(l=>l.pointGroupVisibility),t=v(l=>l.setPointGroupVisibility),a=v(l=>l.coloringStrategy),r=p.useMemo(()=>Object.values(e).every(l=>!l),[e]),i=p.useCallback(l=>{const{checked:o}=l.target,d=Object.keys(e).reduce((c,m)=>(c[m]=o,c),{});t(d)},[e,t]);return s("label",{css:()=>u`
        display: flex;
        flex-direction: row;
        gap: var(--px-flex-gap-sm);
        padding: var(--px-spacing-sm) var(--px-spacing-med);
        background-color: var(--ac-global-background-color-light);
      `,children:[n("input",{type:"checkbox",checked:!r,onChange:i}),`${a}`]})}function Nl(){const{referenceInferences:e,corpusInferences:t}=Ve(),a=v(g=>g.coloringStrategy),r=v(g=>g.setColoringStrategy),i=v(g=>g.dimension),l=v(g=>g.dimensionMetadata),o=v(g=>g.setDimension),d=e!=null||t!=null,c=a===S.dimension&&i==null,m=a===S.dimension&&i!=null&&l==null,h=a!==S.inferences&&!c&&!m;return s("section",{css:u`
        & > .ac-form {
          padding: var(--px-spacing-med) var(--px-spacing-med) 0
            var(--px-spacing-med);
        }
        & > .ac-alert {
          margin: var(--px-spacing-med);
        }
      `,children:[n(Ne,{children:s(Fe,{children:[n(ai,{strategy:a,onChange:r}),a===S.dimension?n(Yr,{selectedDimension:null,onChange:g=>{o(g)}}):null]})}),d?n(ii,{hasReference:e!=null,hasCorpus:t!=null}):null,h?n(li,{}):null,c?n(ca,{variant:"info",showIcon:!1,children:"Please select a dimension to color the point cloud by"}):null,m?n("div",{css:u`
            padding: var(--px-spacing-med);
            min-height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
          `,children:n(ir,{message:"Calculating point colors"})}):null]})}function si(e){return typeof e=="string"&&e in ce}function Vl(e){return s(_e,{defaultValue:e.mode,variant:"inline-button",onChange:t=>{if(si(t))e.onChange(t);else throw new Error(`Unknown view mode: ${t}`)},children:[n(A,{label:"List",value:ce.list,children:n(I,{svg:n(M.ListOutline,{})})}),n(A,{label:"Grid",value:ce.gallery,children:n(I,{svg:n(M.Grid,{})})})]})}function Rl(e){const{driftRatio:t,primaryToCorpusRatio:a,clusterId:r,isSelected:i,onClick:l,onMouseEnter:o,onMouseLeave:d,metricName:c,primaryMetricValue:m,referenceMetricValue:h,hideReference:g}=e,{percentage:f,comparisonInferencesRole:y}=p.useMemo(()=>typeof a=="number"?{percentage:(a+1)/2*100,comparisonInferencesRole:z.corpus}:typeof t=="number"?{percentage:(t+1)/2*100,comparisonInferencesRole:z.reference}:{percentage:100,comparisonInferencesRole:null},[t,a]);return s("div",{css:u`
        border: 1px solid var(--ac-global-border-color-light);
        border-radius: var(--ac-global-rounding-medium);
        overflow: hidden;
        transition: background-color 0.2s ease-in-out;
        cursor: pointer;
        &:hover {
          background-color: var(--ac-global-color-primary-700);
          border-color: var(--ac-global-color-primary);
        }
        &.is-selected {
          border-color: var(--ac-global-color-primary);
          background-color: var(--ac-global-color-primary-700);
        }
      `,className:i?"is-selected":"",role:"button",onClick:l,onMouseEnter:o,onMouseLeave:d,children:[s("div",{css:u`
          padding: var(--ac-global-dimension-static-size-100);
          display: flex;
          flex-direction: row;
          justify-content: space-between;
          align-items: center;
        `,children:[n(F,{"data-testid":"cluster-description",direction:"column",gap:"size-50",alignItems:"start",children:s(F,{direction:"column",alignItems:"start",children:[n(R,{level:3,children:`Cluster ${r}`}),n(k,{color:"text-700",textSize:"small",children:`${e.numPoints} points`})]})}),s("div",{"data-testid":"cluster-metric",css:u`
            display: flex;
            flex-direction: column;
            align-items: end;
          `,children:[n(k,{color:"text-700",textSize:"small",children:c}),n(k,{color:"text-900",textSize:"medium",children:bn(m)}),g?null:n(k,{color:"designationPurple",textSize:"small",children:bn(h)})]})]}),n(ci,{primaryPercentage:f,comparisonInferencesRole:y})]})}function ci({primaryPercentage:e,comparisonInferencesRole:t}){return s("div",{"data-testid":"inferences-distribution",css:u`
        display: flex;
        flex-direction: row;
      `,children:[n("div",{"data-testid":"primary-distribution",css:u`
          background-image: linear-gradient(
            to right,
            var(--px-primary-color--transparent) 0%,
            var(--px-primary-color)
          );
          height: var(--px-gradient-bar-height);
          width: ${e}%;
        `}),n("div",{"data-testid":"reference-distribution","data-reference-inferences-role":`${t??"none"}`,css:u`
          &[data-reference-inferences-role="reference"] {
            background-image: linear-gradient(
              to right,
              var(--px-reference-color) 0%,
              var(--px-reference-color--transparent)
            );
          }
          &[data-reference-inferences-role="corpus"] {
            background-image: linear-gradient(
              to right,
              var(--px-corpus-color) 0%,
              var(--px-corpus-color--transparent)
            );
          }

          height: var(--px-gradient-bar-height);
          width: ${100-e}%;
        `})]})}const di=s(W,{children:[n(R,{weight:"heavy",level:4,children:"UMAP N Neighbors"}),n(Z,{children:n(k,{children:"This parameter controls how UMAP balances local versus global structure in the data. It does this by constraining the size of the local neighborhood UMAP will look at when attempting to learn the manifold structure of the data. This means that low values of n_neighbors will force UMAP to concentrate on very local structure (potentially to the detriment of the big picture), while large values will push UMAP to look at larger neighborhoods of each point when estimating the manifold structure of the data, losing fine detail structure for the sake of getting the broader of the data."})}),n("footer",{children:n(ke,{href:"https://umap-learn.readthedocs.io/en/latest/parameters.html#n-neighbors",children:"View UMAP documentation"})})]}),ui=s(W,{children:[n(R,{weight:"heavy",level:4,children:"UMAP Minimum Distance"}),n(Z,{children:n(k,{children:"The min_dist parameter controls how tightly UMAP is allowed to pack points together. It, quite literally, provides the minimum distance apart that points are allowed to be in the low dimensional representation. This means that low values of min_dist will result in clumpier embeddings. This can be useful if you are interested in clustering, or in finer topological structure. Larger values of min_dist will prevent UMAP from packing points together and will focus on the preservation of the broad topological structure instead."})}),n("footer",{children:n(ke,{href:"https://umap-learn.readthedocs.io/en/latest/parameters.html#min-dist",children:"View UMAP documentation"})})]}),mi=s(W,{children:[n(R,{weight:"heavy",level:4,children:"Number of Samples"}),s(Z,{children:[n(k,{elementType:"p",children:"Determines the number of samples from each inferences to use when projecting the point cloud using UMAP. This number is per-inferences so a value of 500 means that the point cloud will contain up to 1000 points."}),n("br",{}),n(k,{elementType:"p",children:"For best results keep this value low until you have identified a sample that you would like to analyze in more detail."})]})]});function Ol(){const e=v(c=>c.umapParameters),t=v(c=>c.setUMAPParameters),{handleSubmit:a,control:r,setError:i,formState:{isDirty:l,isValid:o}}=qe({reValidateMode:"onChange",defaultValues:e}),d=p.useCallback(c=>{const m=parseFloat(c.minDist);if(m<un||m>mn){i("minDist",{message:`must be between ${un} and ${mn}`});return}t({minDist:m,nNeighbors:parseInt(c.nNeighbors,10),nSamples:parseInt(c.nSamples,10)})},[t,i]);return n("section",{css:u`
        & > .ac-form {
          padding: var(--px-spacing-med) var(--px-spacing-med) 0
            var(--px-spacing-med);
        }
      `,children:s(Ne,{onSubmit:a(d),children:[n(B,{name:"minDist",control:r,rules:{required:"field is required"},render:({field:{onChange:c,onBlur:m,value:h},fieldState:{invalid:g,error:f}})=>n(Q,{label:"min distance",labelExtra:ui,type:"number",description:"how tightly to pack points",errorMessage:f==null?void 0:f.message,validationState:g?"invalid":"valid",onChange:y=>c(parseFloat(y)),onBlur:m,value:h.toString()})}),n(B,{name:"nNeighbors",control:r,rules:{required:"n neighbors is required",min:{value:cn,message:`greater than or equal to ${cn}`},max:{value:dn,message:`less than or equal to ${dn}`}},render:({field:c,fieldState:{invalid:m,error:h}})=>n(Q,{label:"n neighbors",labelExtra:di,type:"number",step:"0.01",description:"balances local versus global structure",errorMessage:h==null?void 0:h.message,validationState:m?"invalid":"valid",...c,value:c.value})}),n(B,{name:"nSamples",control:r,rules:{required:"n samples is required",max:{value:gn,message:`must be below ${gn}`},min:{value:pn,message:`must be above ${pn}`}},render:({field:{onChange:c,onBlur:m,value:h},fieldState:{invalid:g,error:f}})=>n(Q,{label:"n samples",labelExtra:mi,defaultValue:"500",type:"number",description:"number of points to use per inferences",errorMessage:f==null?void 0:f.message,validationState:g?"invalid":"valid",onChange:y=>c(parseInt(y,10)),onBlur:m,value:h.toString()})}),n("div",{css:u`
            display: flex;
            flex-direction: row;
            justify-content: flex-end;
            margin-top: var(--px-spacing-med);
          `,children:n(H,{variant:l?"primary":"default",type:"submit",isDisabled:!o,css:u`
              width: 100%;
            `,children:"Apply UMAP Parameters"})})]})})}const Ge=2147483647,pi=s(W,{children:[n(R,{weight:"heavy",level:4,children:"Minimum Cluster Size"}),n(Z,{children:n(k,{elementType:"p",children:"The primary parameter to effect the resulting clustering is min_cluster_size. Ideally this is a relatively intuitive parameter to select – set it to the smallest size grouping that you wish to consider a cluster."})}),n("footer",{children:n(ke,{href:"https://hdbscan.readthedocs.io/en/latest/parameter_selection.html#selecting-min-cluster-size",children:"View HDBSCAN documentation"})})]}),gi=s(W,{children:[n(R,{weight:"heavy",level:4,children:"Minimum Samples"}),n(Z,{children:n(k,{elementType:"p",children:"The simplest intuition for what min_samples does is provide a measure of how conservative you want you clustering to be. The larger the value of min_samples you provide, the more conservative the clustering – more points will be declared as noise, and clusters will be restricted to progressively more dense areas."})}),n("footer",{children:n(ke,{href:"https://hdbscan.readthedocs.io/en/latest/parameter_selection.html#selecting-min-samples",children:"View HDBSCAN documentation"})})]}),hi=s(W,{children:[n(R,{weight:"heavy",level:4,children:"Cluster Selection Epsilon"}),n(Z,{children:n(k,{elementType:"p",children:"In some cases, we want to choose a small min_cluster_size because even groups of few points might be of interest to us. However, if our data set also contains partitions with high concentrations of objects, this parameter setting can result in a large number of micro-clusters. Selecting a value for cluster_selection_epsilon helps us to merge clusters in these regions. Or in other words, it ensures that clusters below the given threshold are not split up any further."})}),n("footer",{children:n(ke,{href:"https://hdbscan.readthedocs.io/en/latest/parameter_selection.html#selecting-cluster-selection-epsilon",children:"View HDBSCAN documentation"})})]});function Kl(){const e=v(m=>m.hdbscanParameters),t=v(m=>m.setHDBSCANParameters),a=v(m=>m.clustersLoading),{control:r,handleSubmit:i,formState:{isDirty:l,isValid:o},reset:d}=qe({defaultValues:e}),c=p.useCallback(m=>{const h={minClusterSize:parseInt(m.minClusterSize,10),clusterMinSamples:parseInt(m.clusterMinSamples,10),clusterSelectionEpsilon:parseFloat(m.clusterSelectionEpsilon)};t(h),d(h)},[t,d]);return n("section",{css:u`
        & > .ac-form {
          padding: var(--px-spacing-med) var(--px-spacing-med) 0
            var(--px-spacing-med);
        }
      `,children:s(Ne,{onSubmit:i(c),children:[n(B,{name:"minClusterSize",control:r,rules:{required:"field is required",min:{value:Ta,message:"must be greater than 1"},max:{value:Ge,message:"must be less than 2,147,483,647"}},render:({field:{onChange:m,onBlur:h,value:g},fieldState:{invalid:f,error:y}})=>n(Q,{label:"min cluster size",labelExtra:pi,type:"number",description:"the smallest size for a cluster",errorMessage:y==null?void 0:y.message,validationState:f?"invalid":"valid",onChange:b=>m(parseInt(b,10)),onBlur:h,value:g.toString()})}),n(B,{name:"clusterMinSamples",control:r,rules:{required:"field is required",min:{value:hn,message:`must be greater than ${hn}`},max:{value:Ge,message:"must be less than 2,147,483,647"}},render:({field:{onBlur:m,onChange:h,value:g},fieldState:{invalid:f,error:y}})=>n(Q,{label:"cluster minimum samples",labelExtra:gi,type:"number",description:"determines if a point is a core point",errorMessage:y==null?void 0:y.message,validationState:f?"invalid":"valid",onChange:b=>h(parseInt(b,10)),onBlur:m,value:g.toString()})}),n(B,{name:"clusterSelectionEpsilon",control:r,rules:{required:"field is required",min:{value:0,message:"must be a non-negative number"},max:{value:Ge,message:"must be less than 2,147,483,647"}},render:({field:{onBlur:m,onChange:h,value:g},fieldState:{invalid:f,error:y}})=>n(Q,{label:"cluster selection epsilon",labelExtra:hi,type:"number",description:"A distance threshold",errorMessage:y==null?void 0:y.message,validationState:f?"invalid":"valid",onChange:b=>h(parseInt(b,10)),onBlur:m,value:g.toString()})}),n("div",{css:u`
            display: flex;
            flex-direction: row;
            justify-content: flex-end;
            margin-top: var(--px-spacing-med);
          `,children:n(H,{variant:l?"primary":"default",type:"submit",isDisabled:!o,loading:a,css:u`
              width: 100%;
            `,children:a?"Applying parameters":"Apply Clustering Config"})})]})})}const zl=u`
  transition: 250ms linear all;
  background-color: var(--ac-global-color-grey-200);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.8px;
  --px-resize-handle-size: 8px;
  --px-resize-icon-width: 24px;
  --px-resize-icon-height: 2px;
  outline: none;
  &[data-panel-group-direction="vertical"] {
    height: var(--px-resize-handle-size);
    flex-direction: column;
    &:before,
    &:after {
      width: var(--px-resize-icon-width);
      height: var(--px-resize-icon-height);
    }
  }
  &[data-panel-group-direction="horizontal"] {
    width: var(--px-resize-handle-size);
    flex-direction: row;
    &:before,
    &:after {
      width: var(--px-resize-icon-height);
      height: var(--px-resize-icon-width);
    }
  }

  &:hover {
    background-color: var(--ac-global-color-grey-300);
    border-radius: 4px;
    &:before,
    &:after {
      background-color: var(--ac-global-color-primary);
    }
  }

  &:before,
  &:after {
    content: "";
    color: var(--color-solid-resize-bar);
    flex: 0 0 1rem;
    border-radius: 6px;
    background-color: var(--ac-global-color-grey-300);
    flex: none;
  }
`,Al=e=>u`
  transition: 250ms linear all;
  background-color: var(--ac-global-color-grey-200);
  --px-resize-handle-size: 4px;
  outline: none;
  &[data-panel-group-direction="vertical"] {
    height: var(--px-resize-handle-size);
  }
  &[data-panel-group-direction="horizontal"] {
    width: var(--px-resize-handle-size);
  }

  &:hover {
    background-color: ${e.colors.arizeLightBlue};
  }
`;function $l(e){return n("div",{css:u`
        background-color: var(--ac-global-color-grey-200);
        border: 1px solid var(--ac-global-color-grey-300);
        padding: var(--px-spacing-med);
        border-radius: var(--ac-global-rounding-medium);
        display: flex;
        flex-direction: column;
        gap: var(--px-spacing-sm);
        min-width: 200px;
      `,children:e.children})}function Gl(e){return s("div",{css:u`
        display: flex;
        flex-direction: row;
        justify-content: space-between;
      `,children:[s("div",{css:u`
          display: flex;
          flex-direction: row;
          gap: var(--px-spacing-med);
          align-items: center;
        `,children:[n(yi,{color:e.color,shape:e.shape??"line"}),n(k,{children:e.name})]}),n(k,{children:e.value})]})}function Bl(){return n("div",{css:u`
        height: 1px;
        background-color: var(--ac-global-color-grey-300);
        width: 100%;
      `})}const fi=e=>{if(e==="line")return u`
      width: 8px;
      height: 2px;
    `;if(e==="circle")return u`
      width: 8px;
      height: 8px;
      border-radius: 50%;
    `;if(e==="square")return u`
      width: 8px;
      height: 8px;
    `};function yi({color:e,shape:t="line"}){return n("div",{css:u(fi(t),u`
          background-color: ${e};
          flex: none;
        `)})}const Ql={dataKey:"timestamp",stroke:"var(--ac-global-colo-grey-400)",style:{fill:"var(--ac-global-text-color-700)"},scale:"time",type:"number",domain:["auto","auto"],padding:"gap"},Ul={stroke:"var(--ac-global-color-grey-900)",label:{value:"▼",position:"top",style:{fill:"#fabe32",fontSize:da.typography.sizes.small.fontSize}}},Hl={cursor:{fill:"var(--ac-global-color-grey-300)"}},ve=60,be=ve*24,Be=2*be;function jl(e){const{start:t,end:a}=e,r=Math.floor((a.valueOf()-t.valueOf())/1e3/60/60);return r<=1?{evaluationWindowMinutes:1,samplingIntervalMinutes:1}:r<=24?{evaluationWindowMinutes:ve,samplingIntervalMinutes:ve}:{evaluationWindowMinutes:be,samplingIntervalMinutes:be}}function ql(e){const{start:t,end:a}=e,r=Math.floor((a.valueOf()-t.valueOf())/1e3/60/60);return r<=1?{evaluationWindowMinutes:Be,samplingIntervalMinutes:1}:r<=24?{evaluationWindowMinutes:Be,samplingIntervalMinutes:ve}:{evaluationWindowMinutes:Be,samplingIntervalMinutes:be}}function vi(e){let t;return e<ve?t="%H:%M %p":e<be?t="%x %H:%M %p":t="%-m/%-d",t}function Zl(e){const t=e.samplingIntervalMinutes;return p.useMemo(()=>Ee(vi(t)),[t])}const bi=Object.freeze({blue100:"#A4C7E0",blue200:"#7EB0D2",blue300:"#5899C5",blue400:"#3C80AE",blue500:"#2F6488",orange100:"#FECC95",orange200:"#FDB462",orange300:"#FC9C31",orange400:"#F78403",orange500:"#C46903",purple100:"#BEBADA",purple200:"#9E98C8",purple300:"#7F77B6",purple400:"#6157A3",purple500:"#4D4581",pink100:"#FCCDE5",pink200:"#F99FCD",pink300:"#F66FB4",pink400:"#F33F9B",pink500:"#F10E82",gray100:"#f0f0f0",gray200:"#d9d9d9",gray300:"#bdbdbd",gray400:"#969696",gray500:"#737373",gray600:"#525252",gray700:"#252525",default:"#ffffff",primary:"#9efcfd",reference:"#baa1f9"}),Li=Object.freeze({default:"#000000",blue100:"#2F6488",blue200:"#3C80AE",blue300:"#5899C5",blue400:"#7EB0D2",blue500:"#A4C7E0",orange100:"#C46903",orange200:"#F78403",orange300:"#FC9C31",orange400:"#FDB462",orange500:"#FECC95",purple100:"#4D4581",purple200:"#6157A3",purple300:"#7F77B6",purple400:"#9E98C8",purple500:"#BEBADA",pink100:"#F10E82",pink200:"#F33F9B",pink300:"#F66FB4",pink400:"#F99FCD",pink500:"#FCCDE5",gray100:"#252525",gray200:"#525252",gray300:"#737373",gray400:"#969696",gray500:"#bdbdbd",gray600:"#d9d9d9",gray700:"#f0f0f0",primary:"#00add0",reference:"#4500d9"}),Wl=()=>{const{theme:e}=G();return p.useMemo(()=>e==="dark"?bi:Li,[e])};function Xl(e){switch(e.__typename){case"NominalBin":return e.name;case"IntervalBin":return`${Ue(e.range.start)} - ${Ue(e.range.end)}`;case"MissingValueBin":return"(empty)";case"%other":throw new Error("Unexpected bin type %other");default:P()}}function ki(e){return typeof e=="string"&&e in se}function Jl(e){return s(_e,{defaultValue:e.size,variant:"inline-button",onChange:t=>{if(ki(t))e.onChange(t);else throw new Error(`Unknown grid size: ${t}`)},children:[n(A,{label:"Small",value:se.small,children:"S"}),n(A,{label:"Medium",value:se.medium,children:"M"}),n(A,{label:"Large",value:se.large,children:"L"})]})}function Yl(e){const{message:t,...a}=e;return n("div",{css:u`
        width: 100%;
        display: flex;
        justify-content: center;
      `,children:s("div",{css:r=>u`
          margin: ${r.spacing.margin24}px;
          display: flex;
          flex-direction: column;
          align-items: center;
        `,children:[n(ua,{...a}),t&&n(k,{children:t})]})})}class eo extends j.Component{constructor(t){super(t),this.state={hasError:!1}}static getDerivedStateFromError(t){return{hasError:!0}}componentDidCatch(t,a){}render(){return this.state.hasError?n("h1",{children:"Something went wrong."}):this.props.children}}const mt=p.createContext(null);function pt(){let e=p.useContext(mt);return e===null&&(console.warn("useMarkdownMode must be used within a MarkdownDisplayProvider"),e={mode:"text",setMode:()=>{}}),e}function no(e){const t=sn(i=>i.markdownDisplayMode),a=sn(i=>i.setMarkdownDisplayMode),r=p.useCallback(i=>{p.startTransition(()=>{a(i)})},[a]);return n(mt.Provider,{value:{mode:t,setMode:r},children:e.children})}const Ci=u`
  a {
    color: var(--ac-global-color-primary);
    &:visited {
      color: var(--ac-global-color-purple-900);
    }
  }
`;function xi({children:e,mode:t}){return t==="markdown"?n("div",{css:Ci,children:n(Xt,{remarkPlugins:[Jt],children:e})}):n("pre",{css:u`
        white-space: pre-wrap;
        text-wrap: wrap;
        margin: 0;
      `,children:e})}function to({children:e}){const{mode:t}=pt();return n(xi,{mode:t,children:e})}function Si({mode:e,onModeChange:t}){return s(_e,{size:"compact",variant:"inline-button",value:e,onChange:a=>{t(a)},children:[n(A,{label:"text",value:"text",children:s($,{placement:"top",delay:1e3,offset:10,children:[n(te,{children:n(I,{svg:n(ma,{})})}),n(ae,{children:"Text"})]})}),n(A,{label:"markdown",value:"markdown",children:s($,{placement:"top",delay:1e3,offset:10,children:[n(te,{children:n(I,{svg:n(pa,{})})}),n(ae,{children:"Markdown"})]})})]})}function ao(){const{mode:e,setMode:t}=pt();return n(Si,{mode:e,onModeChange:t})}function gt({latencyMs:e,textSize:t="medium"}){const a=p.useMemo(()=>e<3e3?"green-1200":e<8e3?"yellow-1200":e<12e3?"orange-1200":"red-1200",[e]),r=p.useMemo(()=>e<10?ye(e)+"ms":ye(e/1e3)+"s",[e]);return s(F,{direction:"row",alignItems:"center",justifyContent:"start",gap:"size-50",children:[n(k,{color:a,textSize:t,children:n(I,{svg:n(M.ClockOutline,{})})}),n(k,{color:a,textSize:t,children:r})]})}function wi(e){const{spanKind:t}=e,a=p.useMemo(()=>{let r="grey-500";switch(t){case"llm":r="orange-1000";break;case"chain":r="blue-1000";break;case"retriever":r="seafoam-1000";break;case"reranker":r="celery-1000";break;case"embedding":r="indigo-1000";break;case"agent":r="grey-900";break;case"tool":r="yellow-1200";break;case"evaluator":r="indigo-1200";break;case"guardrail":r="fuchsia-1200";break}return r},[t]);return n(Ze,{color:a,children:t})}function Mi(e){switch(e){case"OK":return"success";case"ERROR":return"danger";case"UNSET":return"grey-500";default:P()}}function ht({statusCode:e}){let t=n(M.MinusCircleOutline,{});const a=Mi(e);switch(e){case"OK":t=n(M.CheckmarkCircleOutline,{});break;case"ERROR":t=n(M.AlertCircleOutline,{});break;case"UNSET":t=n(M.MinusCircleOutline,{});break;default:P()}return n(I,{svg:t,color:a,"aria-label":e})}function ro(e){const{name:t,latencyMs:a,spanKind:r,statusCode:i,tokenCountTotal:l,tokenCountPrompt:o,tokenCountCompletion:d}=e;return n(V,{height:"size-500",width:"100%",children:s(F,{direction:"row",gap:"size-150",width:"100%",height:"100%",alignItems:"center",children:[n(wi,{spanKind:r}),n(V,{flex:"1 1 auto",children:n("div",{css:u`
              float: left;
            `,children:n(k,{children:t})})}),typeof l=="number"?n(Vn,{tokenCountTotal:l,tokenCountPrompt:o??0,tokenCountCompletion:d??0}):null,a===null?null:n(gt,{latencyMs:a}),i==="ERROR"?n(ht,{statusCode:"ERROR"}):null]})})}const Ti=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor",strokeOpacity:"0.9"}),n("mask",{id:"path-2-inside-1_33_16916",fill:"currentColor",children:n("path",{fillRule:"evenodd",clipRule:"evenodd",d:"M13 8C13 8.64491 12.8779 9.2613 12.6556 9.82732L17.1924 14.3641L14.364 17.1926L9.82706 12.6557C9.26111 12.8779 8.64481 13 8 13C5.23858 13 3 10.7614 3 8C3 7.13361 3.22036 6.31869 3.60809 5.60822L6 8L7.5 7.50016L8 6.00016L5.60803 3.60819C6.31854 3.2204 7.13353 3 8 3C10.7614 3 13 5.23858 13 8Z"})}),n("path",{d:"M12.6556 9.82732L11.7248 9.46171L11.4853 10.0713L11.9485 10.5344L12.6556 9.82732ZM17.1924 14.3641L17.8995 15.0713L18.6066 14.3641L17.8995 13.657L17.1924 14.3641ZM14.364 17.1926L13.6569 17.8997L14.364 18.6068L15.0711 17.8997L14.364 17.1926ZM9.82706 12.6557L10.5342 11.9486L10.0711 11.4855L9.4615 11.7249L9.82706 12.6557ZM3.60809 5.60822L4.31518 4.90109L3.37037 3.95634L2.7303 5.12917L3.60809 5.60822ZM6 8L5.29291 8.70713L5.72988 9.14407L6.31613 8.94871L6 8ZM7.5 7.50016L7.81614 8.44888L8.29055 8.29079L8.44869 7.81639L7.5 7.50016ZM8 6.00016L8.94869 6.31639L9.14413 5.73007L8.70711 5.29306L8 6.00016ZM5.60803 3.60819L5.12895 2.73042L3.95616 3.37053L4.90093 4.3153L5.60803 3.60819ZM13.5863 10.1929C13.8537 9.51235 14 8.77206 14 8H12C12 8.51776 11.9021 9.01026 11.7248 9.46171L13.5863 10.1929ZM17.8995 13.657L13.3627 9.12022L11.9485 10.5344L16.4853 15.0713L17.8995 13.657ZM15.0711 17.8997L17.8995 15.0713L16.4853 13.657L13.6569 16.4855L15.0711 17.8997ZM9.11995 13.3628L13.6569 17.8997L15.0711 16.4855L10.5342 11.9486L9.11995 13.3628ZM8 14C8.77194 14 9.51211 13.8537 10.1926 13.5865L9.4615 11.7249C9.0101 11.9022 8.51768 12 8 12V14ZM2 8C2 11.3137 4.68629 14 8 14V12C5.79086 12 4 10.2091 4 8H2ZM2.7303 5.12917C2.2644 5.98288 2 6.96206 2 8H4C4 7.30516 4.17633 6.65449 4.48588 6.08727L2.7303 5.12917ZM6.70709 7.29287L4.31518 4.90109L2.901 6.31535L5.29291 8.70713L6.70709 7.29287ZM7.18387 6.55145L5.68387 7.05129L6.31613 8.94871L7.81614 8.44888L7.18387 6.55145ZM7.05132 5.68394L6.55132 7.18394L8.44869 7.81639L8.94869 6.31639L7.05132 5.68394ZM4.90093 4.3153L7.2929 6.70727L8.70711 5.29306L6.31514 2.90109L4.90093 4.3153ZM8 2C6.96197 2 5.98271 2.26444 5.12895 2.73042L6.08712 4.48596C6.65437 4.17636 7.3051 4 8 4V2ZM14 8C14 4.68629 11.3137 2 8 2V4C10.2091 4 12 5.79086 12 8H14Z",fill:"currentColor",fillOpacity:"0.9",mask:"url(#path-2-inside-1_33_16916)"})]}),Ii=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor",strokeOpacity:"0.9"}),n("path",{d:"M4.43782 6.78868L10 3.57735L15.5622 6.78868V13.2113L10 16.4226L4.43782 13.2113V6.78868Z",stroke:"currentColor",strokeOpacity:"0.9"})]}),Di=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor",strokeOpacity:"0.9"}),n("path",{d:"M5 16C5 16 5 11 10 11C15 11 15 16 15 16",stroke:"currentColor",strokeOpacity:"0.9"}),n("rect",{x:"6.5",y:"4.5",width:"7",height:"5",rx:"0.5",stroke:"currentColor",strokeOpacity:"0.9"})]}),Ei=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor",strokeOpacity:"0.9"}),n("path",{fillRule:"evenodd",clipRule:"evenodd",d:"M10 6C10 7.10457 9.10457 8 8 8C6.89543 8 6 7.10457 6 6C6 4.89543 6.89543 4 8 4C9.10457 4 10 4.89543 10 6ZM10.0558 8.18487C9.51887 8.6903 8.7956 9 8 9C7.91155 9 7.824 8.99617 7.7375 8.98867L7.10304 11.2093C8.21409 11.6488 9 12.7326 9 14C9 15.6569 7.65685 17 6 17C4.34315 17 3 15.6569 3 14C3 12.3431 4.34315 11 6 11C6.0409 11 6.08161 11.0008 6.12212 11.0024L6.76944 8.73682C5.72625 8.26703 5 7.21833 5 6C5 4.34315 6.34315 3 8 3C9.65685 3 11 4.34315 11 6C11 6.50075 10.8773 6.97285 10.6604 7.38788L12.1873 8.6094C12.6908 8.22697 13.3189 8 14 8C15.6569 8 17 9.34315 17 11C17 12.6569 15.6569 14 14 14C12.3431 14 11 12.6569 11 11C11 10.3864 11.1842 9.81579 11.5004 9.34053L10.0558 8.18487ZM16 11C16 12.1046 15.1046 13 14 13C12.8954 13 12 12.1046 12 11C12 9.89543 12.8954 9 14 9C15.1046 9 16 9.89543 16 11ZM6 16C7.10457 16 8 15.1046 8 14C8 12.8954 7.10457 12 6 12C4.89543 12 4 12.8954 4 14C4 15.1046 4.89543 16 6 16Z",fill:"currentColor",fillOpacity:"0.9"})]}),Fi=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor",strokeOpacity:"0.9"}),n("path",{d:"M14.65 6.5C14.65 6.98637 14.2466 7.52091 13.379 7.95472C12.5323 8.37806 11.3382 8.65 10 8.65C8.66184 8.65 7.46767 8.37806 6.62099 7.95472C5.75338 7.52091 5.35 6.98637 5.35 6.5C5.35 6.01363 5.75338 5.47909 6.62099 5.04528C7.46767 4.62194 8.66184 4.35 10 4.35C11.3382 4.35 12.5323 4.62194 13.379 5.04528C14.2466 5.47909 14.65 6.01363 14.65 6.5Z",stroke:"currentColor",strokeOpacity:"0.9",strokeWidth:"0.7"}),n("path",{d:"M14.6875 6.83482V9.62479C14.6875 9.62479 13.0769 11.1873 10 11.1873C6.92308 11.1873 5.3125 9.62479 5.3125 9.62479V6.7437",stroke:"currentColor",strokeOpacity:"0.9",strokeWidth:"0.7"}),n("path",{d:"M14.6875 9.625V12.125C14.6875 12.125 13.0769 13.6875 10 13.6875C6.92308 13.6875 5.3125 12.125 5.3125 12.125V9.625",stroke:"currentColor",strokeOpacity:"0.9",strokeWidth:"0.7"}),n("path",{d:"M14.6875 12.125V14.625C14.6875 14.625 13.0769 16.1875 10 16.1875C6.92308 16.1875 5.3125 14.625 5.3125 14.625V12.125",stroke:"currentColor",strokeOpacity:"0.9",strokeWidth:"0.7"})]}),Pi=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor"}),n("path",{d:"M4.5359 10L8 4L11.4641 10H4.5359Z",stroke:"currentColor"}),n("path",{d:"M8.5359 10L12 16L15.4641 10H8.5359Z",stroke:"currentColor"})]}),_i=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor",strokeOpacity:"0.9"}),n("path",{fillRule:"evenodd",clipRule:"evenodd",d:"M10 15C12.7614 15 15 12.7614 15 10C15 7.23858 12.7614 5 10 5C7.23858 5 5 7.23858 5 10C5 12.7614 7.23858 15 10 15ZM10 16C13.3137 16 16 13.3137 16 10C16 6.68629 13.3137 4 10 4C6.68629 4 4 6.68629 4 10C4 13.3137 6.68629 16 10 16Z",fill:"currentColor",fillOpacity:"0.9"})]}),Ni=()=>n("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor",strokeOpacity:"0.9"})}),Vi=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor"}),n("path",{d:"M14.4254 5.58523L15.744 6.87427L15.7249 6.89333L15.7043 6.91394L15.6837 6.93453L15.6631 6.95509L15.6425 6.97562L15.622 6.99612L15.6015 7.01659L15.581 7.03703L15.5606 7.05745L15.5402 7.07783L15.5198 7.09819L15.4995 7.11852L15.4791 7.13882L15.4588 7.15909L15.4386 7.17934L15.4183 7.19956L15.3981 7.21974L15.3779 7.23991L15.3578 7.26004L15.3377 7.28015L15.3176 7.30022L15.2975 7.32028L15.2774 7.3403L15.2574 7.3603L15.2374 7.38027L15.2175 7.40021L15.1975 7.42013L15.1776 7.44002L15.1577 7.45988L15.1379 7.47972L15.118 7.49953L15.0982 7.51931L15.0784 7.53907L15.0587 7.5588L15.0389 7.57851L15.0192 7.59819L14.9996 7.61785L14.9799 7.63748L14.9603 7.65708L14.9407 7.67666L14.9211 7.69621L14.9016 7.71574L14.882 7.73524L14.8625 7.75472L14.8431 7.77417L14.8236 7.7936L14.8042 7.81301L14.7848 7.83239L14.7654 7.85174L14.746 7.87107L14.7267 7.89038L14.7074 7.90966L14.6881 7.92892L14.6689 7.94815L14.6496 7.96736L14.6304 7.98655L14.6113 8.00571L14.5921 8.02485L14.573 8.04397L14.5538 8.06306L14.5347 8.08213L14.5157 8.10118L14.4966 8.1202L14.4776 8.1392L14.4586 8.15818L14.4396 8.17714L14.4207 8.19607L14.4017 8.21498L14.3828 8.23387L14.3639 8.25274L14.3451 8.27158L14.3262 8.2904L14.3074 8.3092L14.2886 8.32798L14.2698 8.34674L14.2511 8.36547L14.2323 8.38418L14.2136 8.40288L14.1949 8.42155L14.1763 8.4402L14.1576 8.45883L14.139 8.47743L14.1204 8.49602L14.1018 8.51459L14.0832 8.53313L14.0647 8.55166L14.0462 8.57016L14.0277 8.58864L14.0092 8.60711L13.9907 8.62555L13.9723 8.64397L13.9538 8.66238L13.9354 8.68076L13.917 8.69913L13.8987 8.71747L13.8803 8.73579L13.862 8.7541L13.8437 8.77239L13.8254 8.79065L13.8071 8.8089L13.7889 8.82713L13.7707 8.84534L13.7524 8.86353L13.7343 8.8817L13.7161 8.89986L13.6979 8.91799L13.6798 8.93611L13.6617 8.95421L13.6436 8.97229L13.6255 8.99036L13.6074 9.0084L13.5894 9.02643L13.5713 9.04444L13.5533 9.06243L13.5353 9.0804L13.5173 9.09836L13.4994 9.1163L13.4814 9.13422L13.4635 9.15213L13.4456 9.17002L13.4277 9.18789L13.4098 9.20574L13.392 9.22358L13.3741 9.2414L13.3563 9.25921L13.3385 9.277L13.3207 9.29477L13.3029 9.31253L13.2852 9.33027L13.2674 9.34799L13.2497 9.3657L13.232 9.38339L13.2143 9.40107L13.1966 9.41873L13.1789 9.43638L13.1613 9.45401L13.1436 9.47163L13.126 9.48923L13.1084 9.50681L13.0908 9.52438L13.0733 9.54194L13.0557 9.55948L13.0381 9.57701L13.0206 9.59452L13.0031 9.61202L12.9856 9.6295L12.9681 9.64697L12.9506 9.66443L12.9332 9.68187L12.9157 9.6993L12.8983 9.71671L12.8809 9.73412L12.8634 9.7515L12.8461 9.76888L12.8287 9.78624L12.8113 9.80358L12.794 9.82092L12.7766 9.83824L12.7593 9.85555L12.742 9.87284L12.7247 9.89013L12.7074 9.9074L12.6901 9.92466L12.6728 9.9419L12.6556 9.95913L12.6383 9.97636L12.6211 9.99356L12.6039 10.0108L12.5867 10.0279L12.5695 10.0451L12.5523 10.0623L12.5351 10.0794L12.518 10.0966L12.5008 10.1137L12.4837 10.1308L12.4666 10.1479L12.4495 10.165L12.4324 10.1821L12.4153 10.1992L12.3982 10.2162L12.3811 10.2333L12.364 10.2503L12.347 10.2674L12.33 10.2844L12.3129 10.3014L12.2959 10.3184L12.2789 10.3354L12.2619 10.3524L12.2449 10.3693L12.2279 10.3863L12.211 10.4032L12.194 10.4202L12.177 10.4371L12.1601 10.454L12.1432 10.471L12.1262 10.4879L12.1093 10.5048L12.0924 10.5216L12.0755 10.5385L12.0586 10.5554L12.0417 10.5723L12.0249 10.5891L12.008 10.606L11.9911 10.6228L11.9743 10.6396L11.9575 10.6565L11.9406 10.6733L11.9238 10.6901L11.907 10.7069L11.8902 10.7237L11.8734 10.7404L11.8566 10.7572L11.8398 10.774L11.823 10.7907L11.8062 10.8075L11.7895 10.8243L11.7727 10.841L11.7559 10.8577L11.7392 10.8745L11.7225 10.8912L11.7057 10.9079L11.689 10.9246L11.6723 10.9413L11.6556 10.958L11.6389 10.9747L11.6221 10.9914L11.6054 11.0081L11.5888 11.0247L11.5721 11.0414L11.5554 11.0581L11.5387 11.0747L11.522 11.0914L11.5054 11.108L11.4887 11.1247L11.4721 11.1413L11.4554 11.1579L11.4388 11.1746L11.4221 11.1912L11.4055 11.2078L11.3888 11.2244L11.3722 11.241L11.3556 11.2576L11.339 11.2742L11.3224 11.2908L11.3057 11.3074L11.2891 11.324L11.2725 11.3406L11.2559 11.3572L11.2393 11.3738L11.2227 11.3903L11.2061 11.4069L11.1895 11.4235L11.173 11.44L11.1564 11.4566L11.1398 11.4732L11.1232 11.4897L11.1066 11.5063L11.0901 11.5228L11.0735 11.5394L11.0569 11.5559L11.0404 11.5725L11.0238 11.589L11.0072 11.6056L10.9907 11.6221L10.9741 11.6386L10.9576 11.6552L10.941 11.6717L10.9245 11.6883L10.9079 11.7048L10.8914 11.7213L10.8748 11.7378L10.8583 11.7544L10.8417 11.7709L10.8252 11.7874L10.8086 11.804L10.7921 11.8205L10.7755 11.837L10.759 11.8535L10.7424 11.8701L10.7259 11.8866L10.7094 11.9031L10.6928 11.9196L10.6763 11.9362L10.6597 11.9527L10.6432 11.9692L10.6266 11.9857L10.6101 12.0023L10.5935 12.0188L10.577 12.0353L10.5604 12.0519L10.5439 12.0684L10.5273 12.0849L10.5108 12.1015L10.4942 12.118L10.4777 12.1345L10.4611 12.1511L10.4446 12.1676L10.428 12.1841L10.4114 12.2007L10.3949 12.2172L10.3783 12.2338L10.3618 12.2503L10.3452 12.2669L10.3286 12.2834L10.312 12.3L10.2955 12.3165L10.2789 12.3331L10.2623 12.3497L10.2457 12.3662L10.2291 12.3828L10.2125 12.3994L10.1959 12.4159L10.1793 12.4325L10.1627 12.4491L10.1461 12.4657L10.1295 12.4823L10.1129 12.4989L10.0963 12.5155L10.0797 12.5321L10.0631 12.5487L10.0464 12.5653L10.0298 12.5819L10.0132 12.5985L9.99652 12.6151L9.97987 12.6318L9.96322 12.6484L9.94657 12.665L9.92991 12.6817L9.91324 12.6983L9.89657 12.715L9.87989 12.7316L9.86321 12.7483L9.84653 12.7649L9.82984 12.7816L9.81314 12.7983L9.79644 12.815L9.77973 12.8317L9.76301 12.8484L9.74629 12.8651L9.72957 12.8818L9.71283 12.8985L9.69609 12.9152L9.67935 12.9319L9.6626 12.9487L9.64584 12.9654L9.62907 12.9822L9.6123 12.9989L9.59552 13.0157L9.57873 13.0324L9.56194 13.0492L9.54514 13.066L9.52833 13.0828L9.51151 13.0996L9.49469 13.1164L9.47786 13.1332L9.46102 13.15L9.44417 13.1668L9.42732 13.1837L9.41045 13.2005L9.39358 13.2174L9.3767 13.2342L9.35981 13.2511L9.34292 13.268L9.32601 13.2849L9.3091 13.3018L9.29217 13.3187L9.27524 13.3356L9.2583 13.3525L9.24135 13.3694L9.22439 13.3864L9.20742 13.4033L9.19044 13.4203L9.17345 13.4372L9.15645 13.4542L9.13945 13.4712L9.12243 13.4882L9.1054 13.5052L9.08836 13.5222L9.07131 13.5393L9.05426 13.5563L9.03719 13.5734L9.02011 13.5904L9.00302 13.6075L8.98592 13.6246L8.9688 13.6417L8.95168 13.6588L8.93455 13.6759L8.9174 13.693L8.90024 13.7101L8.88308 13.7273L8.8659 13.7444L8.84871 13.7616L8.8315 13.7788L8.81429 13.796L8.79706 13.8132L8.77983 13.8304L8.76257 13.8477L8.74531 13.8649L8.72804 13.8821L8.71075 13.8994L8.69345 13.9167L8.67614 13.934L8.65881 13.9513L8.64147 13.9686L8.62412 13.9859L8.60676 14.0033L8.58938 14.0206L8.57199 14.038L8.55458 14.0554L8.53716 14.0728L8.51973 14.0902L8.50229 14.1076L8.48483 14.1251L8.46736 14.1425L8.44987 14.16L8.43237 14.1775L8.41485 14.195L8.39732 14.2125L8.37978 14.23L8.36222 14.2475L8.34465 14.2651L8.32706 14.2827L8.30945 14.3002L8.29184 14.3178L8.2742 14.3355L8.25656 14.3531L8.23889 14.3707L8.22121 14.3884L8.20352 14.4061L8.18581 14.4238L8.16808 14.4415L8.15034 14.4592L8.13258 14.4769L8.11481 14.4947L8.09702 14.5124L8.07921 14.5302L8.06139 14.548L8.04355 14.5658L8.0257 14.5837L8.00783 14.6015L7.98994 14.6194L7.97203 14.6373L7.95411 14.6552L7.93617 14.6731L7.91821 14.691L7.90024 14.709L7.88225 14.727L7.86424 14.7449L7.84621 14.763L7.82817 14.781L7.81011 14.799L7.79203 14.8171L7.77393 14.8352L7.75581 14.8533L7.73768 14.8714L7.71952 14.8895L7.70135 14.9076L7.68316 14.9258L7.66495 14.944L7.64673 14.9622L7.62848 14.9804L7.61022 14.9987L7.59193 15.0169L7.57363 15.0352L7.55531 15.0535L7.53697 15.0718L7.5186 15.0902L7.50022 15.1085L7.48182 15.1269L7.4634 15.1453L7.44496 15.1637L7.4265 15.1822L7.40802 15.2006L7.38952 15.2191L7.371 15.2376L7.35246 15.2561L7.33389 15.2747L7.31531 15.2932L7.29671 15.3118L7.27808 15.3304L7.25944 15.3491L7.24077 15.3677L7.22208 15.3864L7.20337 15.4051L7.18464 15.4238L7.16589 15.4425L7.14712 15.4612L7.12832 15.48L7.10951 15.4988L7.09067 15.5176L7.07181 15.5365L7.05292 15.5553L7.03402 15.5742L7.01509 15.5931L6.99614 15.612C6.27167 16.3357 5.09652 16.3361 4.37259 15.613C3.64838 14.8896 3.64838 13.7168 4.37259 12.9935L13.1214 4.2547L14.4178 5.57764L14.4177 5.57772L14.4254 5.58523Z",stroke:"currentColor"}),n("path",{d:"M12.5299 10.2848L7.32791 15.5545C7.12956 15.7555 6.88934 15.9156 6.62689 16.0225C6.08679 16.2424 5.46752 16.2239 4.94171 15.972L4.77945 16.31L4.94171 15.972C4.6339 15.8246 4.36574 15.6007 4.16736 15.3245L4.02179 15.1219C3.60142 14.5367 3.60138 13.749 4.02169 13.1637C4.12291 13.0228 4.24539 12.8984 4.38476 12.7949L5.72374 11.8006L5.76816 11.7676L5.80115 11.7232L5.91056 11.576C6.30572 11.0443 6.96187 10.4244 7.58765 10.0864C7.90229 9.91646 8.17215 9.83813 8.37711 9.84461C8.55555 9.85025 8.69852 9.9179 8.81563 10.1071C8.88186 10.2141 8.92418 10.3701 8.97238 10.5823C8.97507 10.5942 8.9778 10.6063 8.98058 10.6186C9.00013 10.7052 9.02201 10.8022 9.04751 10.8896C9.07575 10.9865 9.11828 11.1086 9.19239 11.2146C9.29475 11.361 9.4504 11.4075 9.53763 11.4247C9.63768 11.4444 9.74477 11.4446 9.84616 11.436C10.0516 11.4187 10.299 11.3594 10.5607 11.2642C11.0498 11.0864 11.6345 10.7668 12.1516 10.2848L12.5299 10.2848Z",stroke:"currentColor",strokeWidth:"0.75"})]}),Ri=()=>s("svg",{width:"20",height:"20",viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg",children:[n("rect",{x:"0.5",y:"0.5",width:"19",height:"19",rx:"3.5",stroke:"currentColor"}),n("path",{d:"M15.4237 6.90042C15.5191 6.92315 15.6152 6.94413 15.7074 6.96092C15.7135 7.05035 15.7162 7.16454 15.7138 7.30375C15.7056 7.77188 15.6408 8.43317 15.515 9.1653C15.2592 10.6537 14.774 12.3014 14.1 13.2C13.4011 14.1319 12.332 14.9694 11.4101 15.584C10.9538 15.8882 10.5429 16.1317 10.2465 16.2989C10.1617 16.3467 10.0865 16.3882 10.0224 16.423C9.97538 16.3925 9.92211 16.3576 9.86327 16.3183C9.61299 16.1515 9.26304 15.908 8.86735 15.6037C8.07099 14.9911 7.11105 14.148 6.4 13.2C5.71286 12.2838 5.10686 10.6159 4.73507 9.12872C4.55136 8.39389 4.4322 7.73262 4.38844 7.26582C4.37726 7.14653 4.37171 7.04688 4.37029 6.96627C4.68202 6.91822 5.07002 6.82212 5.46167 6.6997C6.04643 6.51692 6.71066 6.25305 7.25513 5.93001C7.78069 5.61819 8.40348 5.00685 8.92133 4.49851C8.96063 4.45994 8.99932 4.42196 9.03732 4.38474C9.32127 4.10667 9.57222 3.86458 9.78023 3.69195C9.86978 3.61763 9.94141 3.56465 9.99619 3.52986C10.0511 3.56629 10.1228 3.62162 10.2126 3.69902C10.4221 3.8796 10.6732 4.13028 10.9589 4.41605L10.9643 4.42138C11.2419 4.69905 11.5471 5.00425 11.8469 5.27159C12.1431 5.53579 12.4648 5.79139 12.7764 5.94721C13.307 6.2125 13.989 6.47149 14.5895 6.66369C14.8912 6.76025 15.179 6.8421 15.4237 6.90042ZM9.92522 3.48908C9.92521 3.48905 9.92594 3.48931 9.92744 3.48994C9.92598 3.48943 9.92523 3.48911 9.92522 3.48908Z",stroke:"currentColor"})]});function Oi({spanKind:e}){let t=n(Ni,{}),a="--ac-global-color-grey-900";switch(e){case"llm":a="--ac-global-color-orange-1000",t=n(Ii,{});break;case"chain":a="--ac-global-color-blue-1000",t=n(_i,{});break;case"retriever":a="--ac-global-color-seafoam-1000",t=n(Fi,{});break;case"embedding":a="--ac-global-color-indigo-1000",t=n(Ei,{});break;case"agent":a="--ac-global-text-color-900",t=n(Di,{});break;case"tool":a="--ac-global-color-yellow-1200",t=n(Ti,{});break;case"reranker":a="--ac-global-color-celery-1000",t=n(Pi,{});break;case"evaluator":a="--ac-global-color-indigo-1000",t=n(Vi,{});break;case"guardrail":a="--ac-global-color-fuchsia-1200",t=n(Ri,{});break}return n("div",{css:u`
        color: var(${a});
        width: 20px;
        height: 20px;
      `,title:e,children:t})}function Ki(e){const t=e.reduce((r,i)=>(r.set(i.context.spanId,{span:i,children:[]}),r),new Map),a=[];for(const r of e){const i=t.get(r.context.spanId);if(r.parentId===null||!t.has(r.parentId))a.push(i);else{const l=t.get(r.parentId);l&&l.children.push(i)}}for(const r of t.values())r.children.sort((i,l)=>new Date(i.span.startTime).valueOf()-new Date(l.span.startTime).valueOf());return a}function io(e){const{spans:t,onSpanClick:a,selectedSpanId:r}=e,i=Ki(t);return n("ul",{css:l=>u`
        margin: ${l.spacing.margin16}px;
        display: flex;
        flex-direction: column;
        gap: ${l.spacing.padding8}px;
      `,children:i.map(l=>n(ft,{node:l,onSpanClick:a,selectedSpanId:r},l.span.context.spanId))})}function ft(e){const{node:t,selectedSpanId:a,onSpanClick:r}=e,i=t.children;return s("div",{children:[n("button",{className:"button--reset",css:u`
          min-width: var(--ac-global-dimension-static-size-4600);
          cursor: pointer;
        `,onClick:()=>{p.startTransition(()=>{r&&r(t.span.context.spanId)})},children:n(zi,{isSelected:a===t.span.context.spanId,children:s(F,{direction:"row",gap:"size-100",justifyContent:"start",alignItems:"center",children:[n(Oi,{spanKind:t.span.spanKind}),n(Gi,{...t.span})]})})}),i.length?n("ul",{css:l=>u`
            margin: var(--ac-global-dimension-static-size-100) 0 0
              var(--ac-global-dimension-static-size-600);
            display: flex;
            flex-direction: column;
            gap: ${l.spacing.padding8}px;
          `,children:i.map((l,o)=>{const d=i[o+1];return s("div",{css:u`
                  position: relative;
                `,children:[d?n(Ai,{...d.span}):null,n($i,{...l.span}),n(ft,{node:l,onSpanClick:r,selectedSpanId:a})]},l.span.context.spanId)})}):null]})}function zi(e){return n("div",{className:e.isSelected?"is-selected":"",css:u`
        border-radius: var(--ac-global-dimension-static-size-150);
        background-color: var(--ac-global-color-grey-200);
        padding: var(--ac-global-dimension-static-size-50)
          var(--ac-global-dimension-static-size-200)
          var(--ac-global-dimension-static-size-50)
          var(--ac-global-dimension-static-size-200);
        border-width: var(--ac-global-dimension-static-size-10);
        border-style: solid;
        border-color: var(--ac-global-color-grey-300);
        &:hover {
          border-color: var(--ac-global-color-grey-400);
          background-color: var(--ac-global-color-grey-300);
        }
        &.is-selected {
          border-color: var(--ac-global-color-primary);
        }
      `,children:e.children})}function Ai({statusCode:e}){return n("div",{"aria-hidden":"true","data-testid":"span-tree-edge-connector",css:t=>u`
        position: absolute;
        border-left: 1px solid
          ${e==="ERROR"?t.colors.statusDanger:"rgb(204, 204, 204)"};
        top: 0;
        left: -22px;
        width: 42px;
        bottom: 0;
      `})}function $i({statusCode:e}){return n("div",{"aria-hidden":"true",css:t=>{const a=e==="ERROR"?t.colors.statusDanger:"rgb(204, 204, 204)";return u`
          position: absolute;
          border-left: 1px solid ${a};
          border-bottom: 1px solid ${a};
          border-radius: 0 0 0 var(--ac-global-dimension-static-size-150);
          top: -24px;
          left: -22px;
          width: 38px;
          height: 48px;
        `}})}function Gi(e){const{name:t,latencyMs:a,statusCode:r,tokenCountTotal:i,tokenCountPrompt:l,tokenCountCompletion:o}=e;return n(V,{height:"size-500",width:"100%",children:s(F,{direction:"row",gap:"size-150",width:"100%",height:"100%",alignItems:"center",children:[n(V,{flex:"1 1 auto",children:n("div",{css:u`
              float: left;
            `,children:n(k,{children:t})})}),typeof i=="number"?n(Vn,{tokenCountTotal:i,tokenCountPrompt:l??0,tokenCountCompletion:o??0}):null,a===null?null:n(gt,{latencyMs:a}),r==="ERROR"?n(ht,{statusCode:"ERROR"}):null]})})}function lo(e){const{theme:t}=G(),a=t==="light"?void 0:Xe;return n(We,{value:e.value,extensions:[Rn(),On.lineWrapping,Kn(zn())],editable:!0,theme:a,...e})}const yt=u`
  .cm-content {
    padding: var(--ac-global-dimension-static-size-200) 0;
  }
  .cm-editor,
  .cm-gutters {
    background-color: transparent;
  }
`;function oo(e){const{theme:t}=G(),a=t==="light"?void 0:Xe;return n(We,{value:e.value,extensions:[Rn(),On.lineWrapping,Kn(zn())],editable:!1,theme:a,...e,basicSetup:{lineNumbers:!0,foldGutter:!0,bracketMatching:!0,syntaxHighlighting:!0,highlightActiveLine:!1,highlightActiveLineGutter:!1},css:yt})}function Bi(e){const{theme:t}=G(),a=t==="light"?void 0:Xe;return n(We,{value:e.value,extensions:[ba()],editable:!1,theme:a,...e,basicSetup:{lineNumbers:!1,foldGutter:!0,bracketMatching:!0,syntaxHighlighting:!0,highlightActiveLine:!1,highlightActiveLineGutter:!1},css:yt})}const vt=function(){var e={defaultValue:null,kind:"LocalArgument",name:"description"},t={defaultValue:null,kind:"LocalArgument",name:"metadata"},a={defaultValue:null,kind:"LocalArgument",name:"name"},r=[{alias:null,args:[{fields:[{kind:"Variable",name:"description",variableName:"description"},{kind:"Variable",name:"metadata",variableName:"metadata"},{kind:"Variable",name:"name",variableName:"name"}],kind:"ObjectValue",name:"input"}],concreteType:"DatasetMutationPayload",kind:"LinkedField",name:"createDataset",plural:!1,selections:[{alias:null,args:null,concreteType:"Dataset",kind:"LinkedField",name:"dataset",plural:!1,selections:[{alias:null,args:null,kind:"ScalarField",name:"id",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"name",storageKey:null},{alias:null,args:null,kind:"ScalarField",name:"description",storageKey:null}],storageKey:null}],storageKey:null}];return{fragment:{argumentDefinitions:[e,t,a],kind:"Fragment",metadata:null,name:"CreateDatasetFormMutation",selections:r,type:"Mutation",abstractKey:null},kind:"Request",operation:{argumentDefinitions:[a,e,t],kind:"Operation",name:"CreateDatasetFormMutation",selections:r},params:{cacheID:"d2aeec21cead6fee265f4e80c330cf18",id:null,metadata:{},name:"CreateDatasetFormMutation",operationKind:"mutation",text:`mutation CreateDatasetFormMutation(
  $name: String!
  $description: String = null
  $metadata: JSON = null
) {
  createDataset(input: {name: $name, description: $description, metadata: $metadata}) {
    dataset {
      id
      name
      description
    }
  }
}
`}}}();vt.hash="06eeac5ef68e9533c4881faad4b4e07d";function so(e){const{onDatasetCreated:t,onDatasetCreateError:a}=e,{control:r,handleSubmit:i,formState:{isDirty:l,isValid:o}}=qe({defaultValues:{name:"Dataset "+new Date().toISOString(),description:"",metadata:{}}}),[d,c]=q.useMutation(vt),m=p.useCallback(h=>{d({variables:h,onCompleted:g=>{t(g.createDataset.dataset)},onError:g=>{a(g)}})},[d,t,a]);return s(Ne,{onSubmit:i(m),children:[s(V,{padding:"size-200",children:[n(B,{name:"name",control:r,rules:{required:"field is required"},render:({field:{onChange:h,onBlur:g,value:f},fieldState:{invalid:y,error:b}})=>n(Q,{label:"Dataset Name",description:"The name of the dataset",errorMessage:b==null?void 0:b.message,validationState:y?"invalid":"valid",onChange:h,onBlur:g,value:f.toString()})}),n(B,{name:"description",control:r,render:({field:{onChange:h,onBlur:g,value:f},fieldState:{invalid:y,error:b}})=>n(ga,{label:"description",isRequired:!1,height:100,errorMessage:b==null?void 0:b.message,validationState:y?"invalid":"valid",onChange:h,onBlur:g,value:f.toString()})})]}),n(V,{paddingEnd:"size-200",paddingTop:"size-100",paddingBottom:"size-100",borderTopColor:"light",borderTopWidth:"thin",children:n(F,{direction:"row",justifyContent:"end",children:n(H,{type:"submit",isDisabled:!o,variant:l?"primary":"default",size:"compact",loading:c,children:c?"Creating...":"Create Dataset"})})})]})}function Tn(e){const t=Date.now(),a=ge(Me(t,365));switch(e){case"1d":return{start:ge(ee(t,1)),end:a};case"7d":return{start:ge(ee(t,7)),end:a};case"30d":return{start:ge(ee(t,30)),end:a};case"all":return{start:new Date("01/01/1971"),end:a};default:P()}}const bt=p.createContext(null);function Qi(){const e=j.useContext(bt);if(e===null)throw new Error("useLastNTimeRange must be used within a LastNTimeRangeProvider");return e}function co({initialTimeRangeKey:e="7d",children:t}){const[a,r]=p.useState(e),[i,l]=p.useState(()=>Tn(e)),o=p.useCallback(d=>{p.startTransition(()=>{r(d),l(Tn(d))})},[]);return n(bt.Provider,{value:{timeRangeKey:a,setTimeRangeKey:o,timeRange:i},children:t})}const Lt=[{key:"1d",label:"Last Day"},{key:"7d",label:"Last 7 Days"},{key:"30d",label:"Last Month"},{key:"all",label:"All Time"}];Lt.reduce((e,t)=>({...e,[t.key]:t}),{});function Ui(e){const{isDisabled:t,selectedKey:a,onSelectionChange:r}=e;return n(Pe,{"aria-label":"Time Range",addonBefore:n(I,{svg:n(M.CalendarOutline,{})}),isDisabled:t,defaultSelectedKey:a,onSelectionChange:i=>{r&&r(i)},align:"end",children:Lt.map(({key:i,label:l})=>n(E,{children:l},i))})}function uo(){const{timeRangeKey:e,setTimeRangeKey:t}=Qi();return n(Ui,{selectedKey:e,onSelectionChange:t})}function mo({indeterminate:e,...t}){const a=p.useRef(null);return j.useEffect(()=>{typeof e=="boolean"&&(a.current.indeterminate=!t.checked&&e)},[a,e,t.checked]),n("div",{onClick:r=>{r.stopPropagation()},children:n("input",{type:"checkbox",ref:a,css:u`
          cursor: pointer;
        `,...t})})}function po({getValue:e}){const t=e();if(!ka(t))throw new Error("TimestampCell only supports number or null values.");const a=t!=null?new Date(t).toLocaleString([],{year:"numeric",month:"numeric",day:"numeric",hour:"2-digit",minute:"2-digit"}):"--";return n("time",{title:t!=null?String(t):"",children:a})}function go(e){return n("button",{className:"button--reset",onClick:t=>{t.stopPropagation(),e.onClick(t)},"aria-label":e["aria-label"],css:u`
        color: var(--ac-global-text-color-white-900);
        .ac-icon-wrap {
          font-size: 1.2rem;
        }

        &:hover {
          color: var(--ac-global-color-primary);
        }
      `,children:n(I,{svg:e.isExpanded?n(M.ChevronDownOutline,{}):n(M.ChevronRightOutline,{})})})}function Hi(){return s("svg",{xmlns:"http://www.w3.org/2000/svg",xmlnsXlink:"http://www.w3.org/1999/xlink",viewBox:"0 0 305.92 350.13",width:28,height:28,css:u`
        .cls-1 {
          fill: url(#linear-gradient);
        }

        .cls-2 {
          fill: url(#Fade_to_Black_2-2);
        }

        .cls-2,
        .cls-3 {
          opacity: 0.5;
        }

        .cls-4 {
          fill: #fedbb5;
        }

        .cls-5 {
          fill: #e5b4a6;
        }

        .cls-6 {
          fill: url(#Fade_to_Black_2);
        }

        .cls-6,
        .cls-7,
        .cls-8,
        .cls-9,
        .cls-10,
        .cls-11,
        .cls-12,
        .cls-13,
        .cls-14 {
          opacity: 0.4;
        }

        .cls-3 {
          fill: url(#linear-gradient-10);
        }

        .cls-7 {
          fill: url(#linear-gradient-6);
        }

        .cls-8 {
          fill: url(#linear-gradient-3);
        }

        .cls-9 {
          fill: url(#linear-gradient-4);
        }

        .cls-10 {
          fill: url(#linear-gradient-2);
        }

        .cls-11 {
          fill: url(#linear-gradient-7);
        }

        .cls-12 {
          fill: url(#linear-gradient-5);
        }

        .cls-13 {
          fill: url(#linear-gradient-8);
        }

        .cls-14 {
          fill: url(#linear-gradient-9);
        }
      `,children:[s("defs",{children:[s("linearGradient",{id:"linear-gradient",x1:"45.77",y1:"21.43",x2:"201.89",y2:"291.83",gradientUnits:"userSpaceOnUse",children:[n("stop",{offset:"0",stopColor:"#18bab6"}),n("stop",{offset:".5",stopColor:"#00adee"}),n("stop",{offset:"1",stopColor:"#0095c4"})]}),s("linearGradient",{id:"linear-gradient-2",x1:"197.65",y1:"237.84",x2:"65.97",y2:"9.77",gradientUnits:"userSpaceOnUse",children:[n("stop",{offset:"0",stopColor:"#fdfdfe",stopOpacity:"0"}),n("stop",{offset:".11",stopColor:"#fdfdfe",stopOpacity:".17"}),n("stop",{offset:".3",stopColor:"#fdfdfe",stopOpacity:".42"}),n("stop",{offset:".47",stopColor:"#fdfdfe",stopOpacity:".63"}),n("stop",{offset:".64",stopColor:"#fdfdfe",stopOpacity:".79"}),n("stop",{offset:".78",stopColor:"#fdfdfe",stopOpacity:".9"}),n("stop",{offset:".91",stopColor:"#fdfdfe",stopOpacity:".97"}),n("stop",{offset:"1",stopColor:"#fdfdfe"})]}),n("linearGradient",{id:"linear-gradient-3",x1:"158.8",y1:"236.43",x2:"63.93",y2:"72.09",xlinkHref:"#linear-gradient-2"}),n("linearGradient",{id:"linear-gradient-4",x1:"145.73",y1:"248.43",x2:"92.77",y2:"156.7",xlinkHref:"#linear-gradient-2"}),n("linearGradient",{id:"linear-gradient-5",x1:"147.93",y1:"266.95",x2:"114.95",y2:"209.83",xlinkHref:"#linear-gradient-2"}),s("linearGradient",{id:"linear-gradient-6",x1:"92.25",y1:"261.75",x2:"92.25",y2:"321.91",gradientUnits:"userSpaceOnUse",children:[n("stop",{offset:"0",stopColor:"#231f20"}),n("stop",{offset:".03",stopColor:"#231f20",stopOpacity:".9"}),n("stop",{offset:".22",stopColor:"#231f20",stopOpacity:".4"}),n("stop",{offset:".42",stopColor:"#231f20",stopOpacity:".1"}),n("stop",{offset:".65",stopColor:"#231f20",stopOpacity:"0"})]}),s("linearGradient",{id:"Fade_to_Black_2","data-name":"Fade to Black 2",x1:"159.88",y1:"256.07",x2:"159.88",y2:"286.75",gradientUnits:"userSpaceOnUse",children:[n("stop",{offset:"0",stopColor:"#231f20"}),n("stop",{offset:"1",stopColor:"#231f20",stopOpacity:"0"})]}),s("linearGradient",{id:"linear-gradient-7",x1:"174.69",y1:"176.58",x2:"174.69",y2:"151.5",gradientUnits:"userSpaceOnUse",children:[n("stop",{offset:"0",stopColor:"#231f20"}),n("stop",{offset:".03",stopColor:"#231f20",stopOpacity:".95"}),n("stop",{offset:".51",stopColor:"#231f20",stopOpacity:".26"}),n("stop",{offset:".81",stopColor:"#231f20",stopOpacity:"0"})]}),s("linearGradient",{id:"linear-gradient-8",x1:"229.53",y1:"195.1",x2:"229.53",y2:"134.41",gradientUnits:"userSpaceOnUse",children:[n("stop",{offset:"0",stopColor:"#231f20"}),n("stop",{offset:".18",stopColor:"#231f20",stopOpacity:".48"}),n("stop",{offset:".38",stopColor:"#231f20",stopOpacity:".12"}),n("stop",{offset:".58",stopColor:"#231f20",stopOpacity:"0"})]}),n("linearGradient",{id:"Fade_to_Black_2-2","data-name":"Fade to Black 2",x1:"286",y1:"242.89",x2:"265.05",y2:"206.61",xlinkHref:"#Fade_to_Black_2"}),n("linearGradient",{id:"linear-gradient-9",x1:"302.87",y1:"232.93",x2:"271.49",y2:"178.58",xlinkHref:"#linear-gradient-2"}),s("linearGradient",{id:"linear-gradient-10",x1:"221.39",y1:"223.73",x2:"267.07",y2:"197.36",gradientUnits:"userSpaceOnUse",children:[n("stop",{offset:"0",stopColor:"#231f20"}),n("stop",{offset:".31",stopColor:"#231f20",stopOpacity:".5"}),n("stop",{offset:".67",stopColor:"#231f20",stopOpacity:".13"}),n("stop",{offset:"1",stopColor:"#231f20",stopOpacity:"0"})]})]}),s("g",{id:"Layer_1-2","data-name":"Layer 1",children:[n("path",{className:"cls-1",d:"m305.42,218.76c-.9-4.06-2.96-7.8-6.14-11.13-1.22-1.28-2.59-2.48-4.07-3.58-.72-.53-1.48-1.03-2.26-1.52-.97-.6-1.98-1.19-3.07-1.75-4.05-2.08-7.5-4.17-10.53-6.41-1.23-.91-2.42-1.86-3.53-2.83-2.71-2.37-4.53-4.38-5.88-6.53-.44-.69-.83-1.44-1.2-2.14-.16-.31-.39-.57-.66-.77-.49-.36-1.12-.52-1.75-.4-.97.18-1.72.97-1.83,1.96-.09.76-.08,1.57.02,2.41.06.5-.2.96-.66,1.17-.11.05-.22.08-.33.09-.64.08-1.23.43-1.6.96-.37.54-.48,1.2-.33,1.83.14.55.32.93.48,1.24l.14.28c.1.19.2.39.31.58.3.57.62,1.15,1,1.71.71,1.04,1.52,2.07,2.46,3.18.3.35.35.86.13,1.27-.22.41-.68.64-1.14.58-5.37-.73-10.17-1.93-14.65-3.59-.51-.19-1.03-.37-1.53-.57-4.02-1.69,3.23-8.92,6.55-14.03,14.55-22.37,17.56-48,17.68-73.93.12-25.07-2.59-49.78-7.57-74.18v-.04c-3.25-20.44-6.01-28.12-7.74-30.97-.37-.76-.78-1.22-1.21-1.45-.48-.32-.73-.17-.73-.17-.93.03-2.01.87-3.3,2.22-5.42,5.71-5.12,12.49-3.62,19.58,6.85,32.22,12.01,64.63,9.66,97.75-1.61,22.83-5.87,44.82-21.82,62.69-.96,1.08-1.99,2.08-3.02,3.1-1.2,1.17-3.04,3.46-4.42,2.51-1.84-1.28-.2-3.9.37-5.25,9.35-21.89,12.04-44.77,10.6-68.36-.03-.55-.09-1.09-.13-1.63l.02-.03c-.04-.44-.08-.85-.12-1.28-.24-3.12-.53-6.23-.92-9.33-4.02-37.42-8.84-39.84-8.84-39.84h0c-.32-.28-.72-.51-1.25-.62-2.53-.53-3.92,1.7-5.04,3.39-5.07,7.6-2.83,15.67-1.19,23.67,5.73,28.01,5.82,55.75-4.02,83-.9,2.48-1.98,4.9-3.12,7.28-1.2,2.53-1.99,5.7-6.12,4.34-3.86-1.28-2.78-4.2-2.27-6.87,1.29-6.79,2.33-13.59,2.98-20.42l.02.04c.06-.67.1-1.32.16-1.98.1-1.18.17-2.36.24-3.54.06-.99.11-1.96.15-2.91.02-.49.04-.97.06-1.46.78-21.63-2.85-31.46-4.23-34.37-.15-.36-.32-.68-.51-.97h0s0,0,0,0c-1.43-2.14-3.8-1.89-5.84.13-3.76,3.72-5.84,8.1-4.88,13.62,2.8,16.09,1.16,32.03-1.84,47.9-.41,2.13-1.36,6-5.9,5.01-3.09-.68-3.81-2.01-3.99-4.69.03-2.03.01-4.05-.06-6.08,0-.05,0-.1,0-.15h0c-.01-.29-.03-.57-.04-.86v-.02c0-.14,0-.27-.02-.4-.13-2.76-.36-5.53-.7-8.3-.03-.27-.08-.53-.12-.79-1.74-15.62-4-17.13-4-17.13-1.45-1.88-3.71-1.57-5.67.38-3.76,3.72-5.67,8.08-4.88,13.62.57,4.06.43,2.81.84,6.34.33,1.82.66,5.13.69,6.19-.09.94-.32,1.76-.9,2.37-1.92,2.07-5.02-.05-7.37-1.02-45.52-18.84-84.49-45.28-118.5-78.71C29.51,74.47,6.74,46.89,6.74,46.89h0c-.84-.99-1.91-1.55-3.53-.85C.24,47.32.33,51.13.06,54.33c-.54,6.41,2.88,11.07,6.62,15.42,51.36,59.92,114.05,102.98,189.7,124.51l13.61,3.61c.16.04.32.08.48.12.03,0,.05.02.07.02l11.72,3.11.32.08c-.38.11-.82.2-1.28.28-12.9,2.55-38.42-2.14-58.91-6.92-10.15-2.13-20.1-4.71-29.85-7.79-.45-.13-.69-.2-.69-.2v-.02c-37.88-12.05-72.58-31.59-102.92-61.4-2.87-2.82-5.54-5.86-8.15-8.95-2.41-2.86-7.36-8.84-9.06-10.89-.19-.27-.39-.51-.6-.73h0s0,0,0,0c-.52-.53-1.14-.87-2.03-.66-2.12.49-2.72,2.67-3.11,4.51-1.55,7.39.8,13.59,5.76,19.15,31.09,34.84,70.09,57.1,113.9,71.7,24.88,8.29,50.46,13.32,76.57,16.54-15.56,5.04-31.58,6.57-47.72,6.17-31.26-.78-60.57-8.29-88.12-21.68-10.16-5.22-19.62-11.05-22.11-12.6-1.43-.98-2.9-1.57-4.36-.45-2.74,2.12-.85,5.85.03,8.76,1.69,5.6,5.58,9.47,10.63,12.14,44.88,23.74,92.26,33.22,142.71,24.8,5.11-.85,9.95-1.79,15.29-3.59-8.43,7.3-18.2,12.06-28.47,15.82-31.59,11.56-62.98,11.09-94.25,3.27-10.03-2.69-21.68-7.05-21.68-7.05h0c-1.68-.73-3.34-.99-4.64.87-2.28,3.27-.29,6.66,1.68,9.74,4.67,7.27,13.68,7.98,20.81,10.44,2.44.77-4.2,5.21-6.34,6.84-10.34,7.91-20.46,15.14-30.76,22.8l-6.74,4.97h0c-1.16.8-2.18,1.69-1.64,3.37.61,1.88,2.57,2.22,4.47,2.62,7.37,1.53,13.66-.92,19.48-5.27,12.48-9.35,25.18-18.41,37.39-28.11,4.64-3.7,8.86-3.39,15.21-1.74-15.88,11.97-30.73,23.17-45.6,34.36-15.08,11.35-30.18,22.7-45.28,34.03l-9.98,7.38c-.15.1-.29.21-.43.32l-.15.11h0c-.85.68-1.48,1.44-1.3,2.44.4,2.25,3.05,2.81,5.21,3.18,8.92,1.54,14.44-1.82,20.54-6.39,30.5-22.9,61.12-45.64,91.44-68.76,6.8-5.18,13.79-8.11,23.61-7.01-8.36,6.25-16.38,12.24-24.3,18.16l-21.51,15.92c-.15.11-.3.22-.45.33h-.02c-1.14.9-1.94,1.96-1.49,3.53.82,2.84,4.24,3.18,7.15,3.62,5.34.8,9.87-1.09,14.06-4.21,2.41-1.8,4.84-3.57,7.28-5.33h0s32.84-26.08,32.84-26.08c0,0,7.76-5.54,16.74-10.64.8-.5,1.61-1,2.41-1.49.34-.15,1.2-.54,2.48-1.16.97-.5,1.93-.99,2.89-1.44,1.41-.72,3.05-1.59,4.88-2.59,5.3-2.2,20.44-9.27,32.98-22.62,5.96-4.6,14.34-10.6,20.87-13.49h0s.04-.02.04-.02c.5-.22.98-.42,1.46-.6h0s.03,0,.06-.02c.32-.12.63-.23.93-.33l.84-.33c2.36-.67,6.22-.92,6.71,4.29.09,1.28.06,2.59-.08,3.97-.11,1.04-.3,2.14-.46,3.02-.15.85.2,1.71.88,2.21.11.08.22.15.34.21.9.44,1.99.24,2.66-.51.25-.28.51-.55.77-.83,3.22-3.38,6.47-5.73,9.95-7.16,5.07-2.1,10.2-2.11,15.68-.02,2.6.99,5.05,2.34,7.48,4.14,1.03.76,2.08,1.62,3.11,2.55.61.56,1.22,1.18,1.76,1.72l.09.09.44.45c.08.08.17.16.26.22.52.38,1.18.53,1.82.39.75-.16,1.37-.69,1.63-1.41.05-.14.1-.28.15-.41,1.56-4.59,1.87-8.82.97-12.93Z"}),n("path",{className:"cls-4",d:"m208.42,169.5c-.37,2.28-.76,4.55-1.19,6.82.43-2.27.82-4.55,1.19-6.82h0Z"}),n("path",{className:"cls-4",d:"m248.79,194.81c.16.07.33.13.5.19-.17-.06-.33-.13-.5-.19"}),n("path",{className:"cls-4",d:"m230.37,180.81s0,0,0,.01c0,0,0,0,0-.01"}),n("path",{className:"cls-4",d:"m230.5,180.5s-.03.06-.04.1c.01-.03.03-.07.04-.1"}),n("path",{className:"cls-4",d:"m255.55,180.46s-.05.08-.08.13c.03-.04.05-.08.08-.13"}),n("path",{className:"cls-4",d:"m215.62,178.85c-.28.59-.54,1.22-.82,1.82.28-.59.54-1.22.82-1.82"}),n("path",{className:"cls-4",d:"m188.53,177.51s.01,0,.02,0c0,0-.01,0-.02,0"}),n("polyline",{className:"cls-4",points:"184.47 175.68 184.47 175.69 184.47 175.68"}),n("polyline",{className:"cls-4",points:"184.45 175.66 184.46 175.66 184.45 175.66"}),n("polyline",{className:"cls-4",points:"184.43 175.62 184.44 175.64 184.43 175.62"}),n("path",{className:"cls-4",d:"m184.42,175.6s0,0,0,.01c0,0,0,0,0-.01"}),n("path",{className:"cls-4",d:"m184.39,175.57s.01.02.02.03c0-.01-.01-.02-.02-.03"}),n("path",{className:"cls-4",d:"m183.65,172.72s0,.01,0,.02c0,0,0-.01,0-.02"}),n("path",{className:"cls-4",d:"m193.79,171c-.08.46-.17.91-.26,1.37.09-.46.17-.91.26-1.37"}),n("path",{className:"cls-4",d:"m168.79,167.86c-.3.32-.63.54-.99.68.35-.14.68-.36.99-.68"}),n("path",{className:"cls-5",d:"m184.47,175.69c.25.35.57.64.99.9h0c-.42-.25-.74-.55-.99-.9m-.02-.03s0,.01.01.02c0,0,0-.01-.01-.02m-.02-.02v.02s0-.01,0-.02m-.01-.02s0,0,0,0c0,0,0,0,0,0m-.01-.01s0,0,0,0c0,0,0,0,0,0m-.02-.04s0,0,0,0c0,0,0,0,0,0m-.74-2.82s0,.01,0,.01c0,0,0,0,0-.01m0-.06h0s0,.03,0,.04c0-.01,0-.02,0-.04m-19.74-4.71s.03.01.04.02c.95.41,1.9.74,2.79.74.37,0,.73-.06,1.06-.19-.34.13-.69.19-1.06.19-.9,0-1.87-.34-2.83-.75m19.61-2.97s0,.01,0,.02c0,0,0-.01,0-.02"}),n("path",{className:"cls-5",d:"m249.29,195c.08.03.16.06.24.09h0c-.08-.03-.16-.06-.24-.09m-18.14-7.32s0,0-.01,0c0,0,.01,0,.01,0m-2.75-1.47c0,.64.22,1.23.85,1.66.23.16.47.23.71.23.38,0,.77-.16,1.17-.41-.4.25-.79.41-1.17.41-.25,0-.49-.07-.72-.23-.63-.43-.85-1.02-.85-1.66m1.33-3.84c-.04.08-.07.17-.11.25.04-.08.07-.17.11-.25m.64-1.54c-.21.51-.42,1.02-.64,1.53.22-.51.43-1.02.64-1.53m.09-.23c-.03.07-.06.14-.09.22.03-.07.06-.14.09-.22m25.01-.01s-.01.02-.02.03c0-.01.01-.02.02-.03m.1-.16s-.01.02-.02.03c0-.01.01-.02.02-.03m-25.03-.01s-.03.06-.04.09c.01-.03.02-.06.04-.09m-23.84-.69c0,1.46.59,2.74,2.81,3.47.68.23,1.28.33,1.8.33,1.87,0,2.77-1.32,3.5-2.85-.73,1.53-1.62,2.85-3.5,2.85-.52,0-1.11-.1-1.8-.33-2.22-.73-2.8-2.01-2.81-3.47m-18.18-2.21h.01-.01m3.63-1.49c-.67.87-1.65,1.51-3.14,1.51-.15,0-.3,0-.46-.02.16.01.31.02.46.02,1.48,0,2.47-.63,3.14-1.51m28.75-10.95s-.01,0-.02,0c-.66,2.17-1.35,4.33-2.13,6.49-.9,2.48-1.98,4.9-3.12,7.28h0c1.13-2.38,2.22-4.8,3.12-7.28.78-2.16,1.5-4.33,2.16-6.49m-25.9-1.2c-.36,2.38-.76,4.75-1.2,7.12.44-2.37.84-4.75,1.2-7.12h0m58.07-11.39s0,0,0,0c-3.26,10.69-8.32,20.76-16.37,29.77-.96,1.08-1.99,2.08-3.02,3.1h0c1.03-1.01,2.06-2.02,3.02-3.1,8.05-9.02,13.12-19.09,16.38-29.78"}),n("path",{className:"cls-10",d:"m4.56,45.73c-.4,0-.85.09-1.34.31-2.11.91-2.68,3.11-2.93,5.45,11.33,14.85,56.07,69.62,126.46,107.18,0,0,68.91,36.38,138.24,40.31-5.37-.73-10.17-1.93-14.65-3.59-.26-.1-.53-.19-.8-.29h0c-25.19-5.44-46.66-12.25-61.84-17.7.29.06.57.1.84.13-.28-.03-.57-.07-.88-.14-.92-.2-1.62-.46-2.17-.79-12.01-4.39-19.66-7.76-21.51-8.59-.88-.38-1.75-.83-2.53-1.15-45.52-18.84-84.49-45.28-118.5-78.71C29.51,74.47,6.74,46.89,6.74,46.89h0c-.58-.68-1.28-1.16-2.18-1.16"}),n("path",{className:"cls-8",d:"m9.57,103.87c-.16,0-.33.02-.51.06-2.12.49-2.72,2.67-3.11,4.51-.07.33-.13.66-.18.99,35.19,47.67,82.41,67.15,82.41,67.15,47.15,22.21,85.84,26.69,109.4,26.69,9.75,0,16.91-.77,21.01-1.37-1.87.21-3.93.31-6.14.31-13.81,0-33.56-3.79-50.06-7.64-10.15-2.13-20.1-4.71-29.85-7.79-.45-.13-.69-.2-.69-.2v-.02c-37.88-12.05-72.58-31.59-102.92-61.4-2.87-2.82-5.54-5.86-8.15-8.95-2.41-2.86-7.36-8.84-9.06-10.89-.19-.27-.39-.51-.6-.73h0s0,0,0,0c-.41-.42-.9-.72-1.53-.72"}),n("path",{className:"cls-9",d:"m41.57,186.66c-.56,0-1.13.18-1.69.61-2.39,1.85-1.26,4.91-.35,7.6,17.64,10.71,58.1,31.53,106.02,31.53,18.09,0,37.24-2.97,56.64-10.57-14,4.54-28.37,6.23-42.87,6.23-1.61,0-3.23-.02-4.85-.06-31.26-.78-60.57-8.29-88.12-21.68-10.16-5.22-19.62-11.05-22.11-12.6-.88-.6-1.78-1.06-2.68-1.06"}),n("path",{className:"cls-12",d:"m205.41,231.93c-7.68,5.89-16.32,9.97-25.34,13.27-16.95,6.2-33.84,8.94-50.68,8.94-14.56,0-29.08-2.05-43.57-5.67-10.03-2.69-21.68-7.05-21.68-7.05h0c-.74-.32-1.47-.55-2.17-.55-.9,0-1.74.38-2.47,1.42-1.06,1.52-1.2,3.07-.85,4.6,11.13,5.17,35,14.36,64.11,14.36,25.24,0,54.41-6.9,82.66-29.31"}),n("path",{className:"cls-7",d:"m130.35,268.02c-27.34,0-48.01-5.54-50.62-6.27.77.23,1.52.46,2.26.71,2.44.77-4.2,5.21-6.34,6.84-7.65,5.85-15.17,11.32-22.73,16.88h23.2c7.31-5.4,14.6-10.84,21.72-16.5,2.65-2.11,5.15-2.91,7.99-2.91,2.15,0,4.48.46,7.22,1.17-15.88,11.97-30.73,23.17-45.6,34.36-8.69,6.54-17.39,13.07-26.09,19.61h23.34c20.99-15.71,41.97-31.42,62.82-47.32,4.81-3.67,9.71-6.2,15.64-6.98-4.39.29-8.67.41-12.8.41Z"}),n("path",{className:"cls-6",d:"m125.47,286.75h22.55l16.66-13.24s7.76-5.54,16.74-10.64c.8-.5,1.61-1,2.41-1.49.34-.15,1.2-.54,2.48-1.16.97-.5,1.93-.99,2.89-1.44,1.46-.75,3.18-1.65,5.09-2.71-16.08,6.73-32.54,10.02-47.79,11.29.21,0,.42,0,.63,0,1.28,0,2.61.07,3.99.23-8.36,6.25-16.38,12.24-24.3,18.16l-1.36,1Z"}),n("path",{className:"cls-11",d:"m183.65,172.69c.03-2.03.01-4.05-.06-6.08v-.15s0,0,0,0c-.01-.29-.03-.57-.04-.86v-.02s-.02-.4-.02-.4c-.08-1.7-.21-3.41-.37-5.12-5.38-2.26-10.45-5.15-15.12-8.56.03.48.05.96.12,1.46.57,4.06.43,2.81.84,6.34.33,1.82.66,5.13.69,6.19-.09.94-.32,1.76-.9,2.37-.59.63-1.29.87-2.05.87-.9,0-1.87-.34-2.83-.75,1.78.8,9.45,4.19,21.55,8.61-1.3-.79-1.69-2.01-1.81-3.9Z"}),n("path",{className:"cls-13",d:"m271.38,134.41c-5.03,7.01-11.24,13.15-18.32,18.08-3.26,10.69-8.32,20.76-16.37,29.77-.96,1.08-1.99,2.08-3.02,3.1-1,.97-2.45,2.73-3.7,2.73-.25,0-.49-.07-.72-.23-1.84-1.28-.2-3.9.37-5.25,3.02-7.06,5.33-14.23,7.04-21.49-5.04,1.89-10.33,3.22-15.79,3.96-.66,2.17-1.35,4.33-2.13,6.49-.9,2.48-1.98,4.9-3.12,7.28-1,2.11-1.72,4.67-4.32,4.67-.52,0-1.11-.1-1.8-.33-3.86-1.28-2.78-4.2-2.27-6.87.67-3.54,1.27-7.08,1.79-10.63-4.8-.15-9.49-.77-14.03-1.82-.43,2.83-.92,5.67-1.46,8.49-.36,1.89-1.16,5.17-4.53,5.17-.4,0-.85-.05-1.33-.15,15.19,5.45,36.66,12.26,61.84,17.71h0c-.25-.1-.5-.19-.74-.29-4.02-1.69,3.23-8.92,6.55-14.03,9.35-14.37,13.92-30.09,16.03-46.36Z"}),n("path",{className:"cls-2",d:"m267.61,212.35c-3.15,0-6.32.3-9.44.88-.59.11-1.17.16-1.72.16-.89,0-1.72-.13-2.5-.37.13.16.25.3.37.47,1.37,1.9,2.08,3.98,2.35,6.14.34.37.63.84.86,1.43h0s0,.02.01.03c0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,0,0,.01,0,0,0,0,0,.01,0,0,0,.01,0,.01,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,0,0,0v.02s0,0,0,.01c0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,0,0,0,0,.02,0,.02,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,0,0,.01,0,.02,0,.03,0,0,0,0,0,0,0,0,0,0,0,.01t0,0s0,.02,0,.03c0,0,0,0,0,0,0,0,0,.02,0,.03,0,0,0,0,0,0,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,0,0,.02,0,0,0,.01,0,.02,0,0,0,.01,0,.01,0,0,0,.01,0,.01,0,0,0,.01,0,.02,0,0,0,.01,0,.01,0,0,0,0,0,.02s0,.01,0,.02c0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,.01,0,.01s0,.01,0,.01c0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,.01,0,0,0,.01,0,.02,0,0,0,0,0,0,0,0,0,.02,0,.03,0,0,0,0,0,0,0,0,0,.02,0,.03,0,0,0,0,0,0,0,0,0,.02,0,.02,0,0,0,0,0,0,0,.01,0,.02,0,.03,0,0,0,0,0,0,0,0,0,.02,0,.03,0,0,0,0,0,0,0,0,0,.02,0,.03h0s0,.03,0,.04h0s0,.02,0,.03h0s0,.03,0,.03h0s0,.03,0,.04h0s0,.02,0,.03h0s0,.02,0,.03h0s0,.02,0,.03h0s0,.02,0,.04c0,0,0,0,0,0,0,.03.01.07.01.1h0s0,.03,0,.04h0s0,.07.01.11h0s0,.02,0,.04h0s0,.03,0,.04h0s0,.05,0,.07h0s0,.02,0,.04h0s0,.03,0,.04h0s0,.03,0,.04h0c.03.5.05,1,.05,1.52,0,.8-.04,1.61-.13,2.46-.11,1.04-.3,2.14-.46,3.02-.02.13-.04.27-.04.4,0,.71.34,1.39.92,1.81l.34.21c.32.16.66.23,1,.23.62,0,1.23-.26,1.67-.74.25-.28.51-.55.77-.83,3.22-3.38,6.47-5.73,9.95-7.16,2.54-1.05,5.1-1.58,7.71-1.58s5.24.52,7.96,1.56c2.6.99,5.05,2.34,7.48,4.14,1.03.76,2.08,1.62,3.11,2.55.61.56,1.22,1.18,1.76,1.72l.09.09.44.45.26.22c.38.28.83.43,1.3.44-2.15-4.61-4.88-8.9-8.73-12.24-7.28-6.31-16.46-8.98-25.8-8.98"}),n("path",{className:"cls-14",d:"m266.74,181.67l-.41.04c-.97.18-1.72.97-1.83,1.96-.09.76-.08,1.57.02,2.41.03.26-.03.52-.16.73,3.89,5.78,12.33,16.03,25.15,19.91,0,0,19.81,10.36,14.8,25.38h0l.15-.41c1.56-4.59,1.87-8.82.97-12.93-.9-4.06-2.96-7.8-6.14-11.13-1.22-1.28-2.59-2.48-4.07-3.58-.72-.53-1.48-1.03-2.26-1.52-.97-.6-1.98-1.19-3.07-1.75-4.05-2.08-7.5-4.17-10.53-6.41-1.23-.91-2.42-1.86-3.53-2.83-2.71-2.37-4.53-4.38-5.88-6.53-.44-.69-.83-1.44-1.2-2.14-.16-.31-.39-.57-.66-.77-.38-.28-.85-.44-1.34-.44"}),n("path",{className:"cls-3",d:"m241.61,223.53l4.01-2.33,16.87-22.61s-9.24-1.75-13.7-3.78c0,0-4.64,21.12-21.73,38.76l6.3-4.67c2.51-1.76,4.79-3.29,8.24-5.37Z"})]})]})}const ji=u`
  padding: var(--px-spacing-med) var(--px-spacing-med) var(--px-spacing-med)
    12px;
  border-bottom: 1px solid var(--ac-global-color-grey-200);
  flex: none;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
`,qi=u`
  padding: var(--px-spacing-lg) var(--px-spacing-med);
  flex: none;
  display: flex;
  flex-direction: column;
  background-color: var(--ac-global-color-grey-75);
  border-right: 1px solid var(--ac-global-color-grey-200);
  box-sizing: border-box;
  height: 100vh;
  position: fixed;
  width: var(--px-nav-collapsed-width);
  z-index: 2; // Above the content
  transition:
    width 0.15s cubic-bezier(0, 0.57, 0.21, 0.99),
    box-shadow 0.15s cubic-bezier(0, 0.57, 0.21, 0.99);
  &[data-expanded="true"] {
    width: var(--px-nav-expanded-width);
    box-shadow: 0 0 30px 0 rgba(0, 0, 0, 0.2);
  }
`,rn=u`
  width: 100%;
  color: var(--ac-global-color-grey-500);
  background-color: transparent;
  border-radius: var(--ac-global-rounding-small);
  display: flex;
  flex-direction: row;
  align-items: center;
  overflow: hidden;
  transition:
    color 0.2s ease-in-out,
    background-color 0.2s ease-in-out;
  text-decoration: none;
  &.active {
    color: var(--ac-global-color-grey-1200);
    background-color: var(--ac-global-color-primary-300);
  }
  &:hover:not(.active) {
    color: var(--ac-global-color-grey-1200);
    background-color: var(--ac-global-color-grey-200);
  }
  & > .ac-icon-wrap {
    padding: var(--ac-global-dimension-size-50);
    display: inline-block;
  }
`,Zi=e=>u`
  color: var(--ac-global-text-color-900);
  font-size: ${e.typography.sizes.large.fontSize}px;
  text-decoration: none;
  margin: 0 0 var(--px-spacing-lg) 0;
`,Wi=()=>n("svg",{xmlns:"http://www.w3.org/2000/svg",width:"20",height:"20",viewBox:"0 0 24 24",children:s("g",{"data-name":"Layer 2",children:[n("rect",{width:"24",height:"24",transform:"rotate(180 12 12)",opacity:"0"}),n("path",{d:"M12 1A10.89 10.89 0 0 0 1 11.77 10.79 10.79 0 0 0 8.52 22c.55.1.75-.23.75-.52v-1.83c-3.06.65-3.71-1.44-3.71-1.44a2.86 2.86 0 0 0-1.22-1.58c-1-.66.08-.65.08-.65a2.31 2.31 0 0 1 1.68 1.11 2.37 2.37 0 0 0 3.2.89 2.33 2.33 0 0 1 .7-1.44c-2.44-.27-5-1.19-5-5.32a4.15 4.15 0 0 1 1.11-2.91 3.78 3.78 0 0 1 .11-2.84s.93-.29 3 1.1a10.68 10.68 0 0 1 5.5 0c2.1-1.39 3-1.1 3-1.1a3.78 3.78 0 0 1 .11 2.84A4.15 4.15 0 0 1 19 11.2c0 4.14-2.58 5.05-5 5.32a2.5 2.5 0 0 1 .75 2v2.95c0 .35.2.63.75.52A10.8 10.8 0 0 0 23 11.77 10.89 10.89 0 0 0 12 1","data-name":"github"})]})});function kt(e){return s("a",{href:e.href,target:"_blank",css:rn,rel:"noreferrer",children:[e.icon,n(k,{children:e.text})]})}function ho(){return n(kt,{href:"https://github.com/arize-ai/phoenix",icon:n(I,{svg:n(Wi,{})}),text:"Repository"})}function fo(){return n(kt,{href:"https://docs.arize.com/phoenix",icon:n(I,{svg:n(M.BookOutline,{})}),text:"Documentation"})}function yo(){const{theme:e,setTheme:t}=G(),a=e==="dark";return s("button",{css:rn,onClick:()=>t(a?"light":"dark"),className:"button--reset",children:[n(I,{svg:a?n(M.MoonOutline,{}):n(M.SunOutline,{})}),n(k,{children:a?"Dark":"Light"})]})}function vo(){return n(En,{to:"/",css:Zi,title:`version: ${window.Config.platformVersion}`,children:n(Hi,{})})}function bo({children:e}){return n("nav",{css:ji,children:e})}function Lo({children:e}){const[t,a]=p.useState(!1);return n("nav",{"data-expanded":t,css:qi,onMouseOver:()=>{a(!0)},onMouseOut:()=>{a(!1)},children:e})}function ko(e){return s(Yt,{to:e.to,css:rn,children:[e.icon,n(k,{children:e.text})]})}function Xi(e){var t;return typeof e.handle=="object"&&typeof((t=e.handle)==null?void 0:t.crumb)=="function"}function Co(){const e=ea(),a=na().filter(Xi);return n(ha,{onAction:r=>{e(a[Number(r)].pathname)},children:a.map((r,i)=>n(E,{children:r.handle.crumb(r.data)},i))})}function xo(e){const{value:t}=e;return s("div",{className:"python-code-block",css:u`
        position: relative;
        .copy-to-clipboard-button {
          position: absolute;
          top: var(--ac-global-dimension-size-100);
          right: var(--ac-global-dimension-size-100);
          z-index: 1;
        }
      `,children:[n(or,{text:t}),n(Bi,{value:t})]})}const Ji=e=>p.useMemo(()=>{const a=e.charCodeAt(0);return Fn(a%26/26)},[e]);function Yi({annotationName:e}){const t=Ji(e);return n("span",{css:u`
        background-color: ${t};
        display: inline-block;
        width: 0.6rem;
        height: 0.6rem;
        border-radius: 2px;
      `})}const In=u`
  display: flex;
  align-items: center;
  .ac-text {
    display: inline-block;
    max-width: 9rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
`;function So({annotation:e,onClick:t}){const a=typeof t=="function",r=typeof e.score=="number"&&ye(e.score)||e.label||"n/a";return s($,{delay:500,offset:3,children:[n(te,{children:n("div",{role:"button",css:u`
            cursor: pointer;
            border-radius: var(--ac-global-dimension-size-50);
            border: 1px solid var(--ac-global-color-grey-400);
            padding: var(--ac-global-dimension-size-50)
              var(--ac-global-dimension-size-100);
            transition: background-color 0.2s;
            &:hover {
              background-color: var(--ac-global-color-grey-300);
            }
            .ac-icon-wrap {
              font-size: 12px;
            }
          `,"aria-label":"Click to view the annotation trace",onClick:i=>{i.stopPropagation(),i.preventDefault(),t&&t()},children:s(F,{direction:"row",gap:"size-100",alignItems:"center",children:[n(Yi,{annotationName:e.name}),n("div",{css:In,children:n(k,{weight:"heavy",textSize:"small",color:"inherit",children:e.name})}),n("div",{css:u(In,u`
                  margin-left: var(--ac-global-dimension-100);
                `),children:n(k,{textSize:"small",children:r})}),e.trace&&a?n(I,{svg:n(M.ArrowIosForwardOutline,{})}):null]})})}),s(fa,{children:[n(k,{weight:"heavy",color:"inherit",textSize:"large",elementType:"h3",children:e.name}),s(V,{paddingTop:"size-50",minWidth:"150px",children:[s(F,{direction:"row",justifyContent:"space-between",children:[n(k,{weight:"heavy",color:"inherit",children:"score"}),n(k,{color:"inherit",children:lt(e.score)})]}),s(F,{direction:"row",justifyContent:"space-between",children:[n(k,{weight:"heavy",color:"inherit",children:"label"}),n(k,{color:"inherit",children:e.label||"--"})]}),s(F,{direction:"row",justifyContent:"space-between",children:[n(k,{weight:"heavy",color:"inherit",children:"kind"}),n(k,{color:"inherit",children:e.annotatorKind})]})]}),e.explanation?n(V,{paddingTop:"size-50",children:s(F,{direction:"column",children:[n(k,{weight:"heavy",color:"inherit",children:"explanation"}),n(V,{maxHeight:"300px",overflow:"auto",children:n(k,{color:"inherit",children:e.explanation})})]})}):null,e.trace&&a?n(V,{paddingTop:"size-100",children:s("div",{css:u`
                display: flex;
                flex-direction: row;
                align-items: center;
                color: var(--ac-global-color-primary);
                gap: var(--ac-global-dimension-size-50);
              `,children:[n(I,{svg:n(M.InfoOutline,{})}),n("span",{children:"Click to view evaluator trace"})]})}):null]})]})}function wo({sequenceNumber:e}){return s(Ze,{color:"yellow-1000",children:["#",e]})}export{Ol as $,ke as A,xl as B,Gl as C,Fa as D,Yl as E,fe as F,dt as G,ce as H,Jl as I,Vl as J,nn as K,ir as L,El as M,Rl as N,Kl as O,bl as P,dl as Q,Le as R,ne as S,vl as T,cl as U,ul as V,ml as W,Fl as X,zl as Y,Il as Z,Nl as _,Qa as a,Al as a0,_l as a1,Za as a2,Hl as a3,Xl as a4,lt as a5,Wa as a6,Dl as a7,ye as a8,or as a9,go as aA,uo as aB,Co as aC,bo as aD,vo as aE,ko as aF,fo as aG,ho as aH,yo as aI,Lo as aJ,pl as aK,sl as aL,co as aM,xo as aN,_a as aO,So as aP,oo as aQ,wl as aR,Yi as aS,Ji as aT,wo as aU,Ja as aV,tr as aW,kl as aX,yl as aY,ll as aZ,gl as a_,ja as aa,Sl as ab,fl as ac,so as ad,lo as ae,io as af,Mi as ag,ht as ah,gt as ai,ro as aj,ol as ak,Oi as al,no as am,ao as an,to as ao,eo as ap,Qi as aq,qa as ar,Pl as as,hl as at,Cl as au,mo as av,wi as aw,tt as ax,po as ay,Ki as az,Ll as b,Ml as c,G as d,Ea as e,v as f,Xn as g,P as h,sr as i,jl as j,ql as k,Zl as l,Ql as m,Ul as n,Wl as o,Qe as p,Bl as q,$l as r,bn as s,at as t,Ve as u,Sr as v,wr as w,Un as x,Fr as y,Tl as z};
