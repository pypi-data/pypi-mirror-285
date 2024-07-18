var w=Object.defineProperty;var S=(i,t,a)=>t in i?w(i,t,{enumerable:!0,configurable:!0,writable:!0,value:a}):i[t]=a;var m=(i,t,a)=>(S(i,typeof t!="symbol"?t+"":t,a),a);function u(i,...t){let a="",e;for(e=0;e<t.length;e++)a+=i[e]+t[e];return a+=i[e],a}const I="X-Api-Key";class g{constructor(t){m(this,"$axios");this.$axios=t}_createAuthorizationHeader(t){return{[I]:t.apiKey}}async post(t,a){if(t!=null)return await this.$axios.post(t.endpoint,a,{headers:this._createAuthorizationHeader(t)})}}class A{constructor(t={}){this.t=t,this.g=new(typeof TextDecoder<"u"?TextDecoder:require("util").TextDecoder)}decode(t){const a=new Uint8Array(t),e=new DataView(a.buffer);return this.D={array:a,view:e},this.S=0,this.C()}C(t=this.m(!1)){switch(t){case"Z":return null;case"N":return;case"T":return!0;case"F":return!1;case"i":return this.F(({view:a},e)=>a.getInt8(e),1);case"U":return this.F(({view:a},e)=>a.getUint8(e),1);case"I":return this.F(({view:a},e)=>a.getInt16(e),2);case"l":return this.F(({view:a},e)=>a.getInt32(e),4);case"L":return this.N(8,this.t.int64Handling,!0);case"d":return this.F(({view:a},e)=>a.getFloat32(e),4);case"D":return this.F(({view:a},e)=>a.getFloat64(e),8);case"H":return this.N(this.V(),this.t.highPrecisionNumberHandling,!1);case"C":return String.fromCharCode(this.C("i"));case"S":return this.j(this.V());case"[":return this.M();case"{":return this.O()}throw Error("Unexpected type")}Z(){let t,a;switch(this.m(!0)){case"$":if(this.q(),t=this.m(!1),this.m(!0)!=="#")throw Error("Expected count marker");case"#":this.q(),a=this.V()}return{type:t,count:a}}M(){const{type:t,count:a}=this.Z();if("ZTF".indexOf(t)!==-1)return Array(a).fill(this.C(t));if(this.t.useTypedArrays)switch(t){case"i":return this.B(a);case"U":return this.L(a);case"I":return Int16Array.from({length:a},()=>this.C(t));case"l":return Int32Array.from({length:a},()=>this.C(t));case"d":return Float32Array.from({length:a},()=>this.C(t));case"D":return Float64Array.from({length:a},()=>this.C(t))}if(a!=null){const e=Array(a);for(let r=0;r<a;r++)e[r]=this.C(t);return e}{const e=[];for(;this.m(!0)!=="]";)e.push(this.C());return this.q(),e}}O(){const{type:t,count:a}=this.Z(),e={};if(a!=null)for(let r=0;r<a;r++)e[this.C("S")]=this.C(t);else{for(;this.m(!0)!=="}";)e[this.C("S")]=this.C();this.q()}return e}V(){const t=this.C();if(Number.isInteger(t)&&t>=0)return t;throw Error("Invalid length/count")}N(t,a,e){if(typeof a=="function")return this.F(a,t);switch(a){case"skip":return void this.q(t);case"raw":return e?this.L(t):this.j(t)}throw Error("Unsuported type")}L(t){return this.F(({array:a},e)=>new Uint8Array(a.buffer,e,t),t)}B(t){return this.F(({array:a},e)=>new Int8Array(a.buffer,e,t),t)}j(t){return this.F(({array:a},e)=>this.g.decode(new DataView(a.buffer,e,t)),t)}q(t=1){this.R(t),this.S+=t}m(t){const{array:a,view:e}=this.D;let r="N";for(;r==="N"&&this.S<a.byteLength;)r=String.fromCharCode(e.getInt8(this.S++));return t&&this.S--,r}F(t,a){this.R(a);const e=t(this.D,this.S,a);return this.S+=a,e}R(t){if(this.S+t>this.D.array.byteLength)throw Error("Unexpected EOF")}}function b(i,t){return new A(t).decode(i)}class T{downloadArrayBuffer(t,a){const e=new Blob([new Uint8Array(a).buffer]),r=window.URL.createObjectURL(e),n=document.createElement("a");n.href=r,n.download=t,document.body.appendChild(n),n.click(),n.remove(),window.URL.revokeObjectURL(r)}}const N=u`query scans($scanIds: [Int], $page: Int, $numberElements: Int, $orderBy: OxoScanOrderByEnum, $sort: SortEnum) {
  scans(scanIds: $scanIds, page: $page, numberElements: $numberElements, orderBy: $orderBy, sort: $sort) {
    pageInfo {
      count
      numPages
    }
    scans {
      id
      title
      createdTime
      progress
      assets {
        __typename
        ... on OxoAndroidFileAssetType {
          id
          packageName
          path
        }
        ... on OxoIOSFileAssetType {
          id
          bundleId
          path
        }
        ... on OxoAndroidStoreAssetType {
          id
          packageName
          applicationName
        }
        ... on OxoIOSStoreAssetType {
          id
          bundleId
          applicationName
        }
        ... on OxoUrlsAssetType {
          id
          links {
            url
            method
          }
        }
        ... on OxoNetworkAssetType {
          id
          networks {
            host
            mask
          }
        }
        ... on OxoDomainNameAssetsType {
          id
          domainNames {
            name
          }
        }
      }
    }
  }
}
`,$=u`
query Scan($scanId: Int!) {
  scan(scanId: $scanId) {
      id
      title
      createdTime
      messageStatus
      progress
  }
}
`,C=u`mutation deleteScan($scanId: Int!) {
  deleteScan(scanId: $scanId) {
    result
  }
}
`,E=u`mutation stopScan($scanId: Int!) {
  stopScan(scanId: $scanId) {
    scan {
      id
    }
  }
}`,x=u`mutation ImportScan($file: Upload!, $scanId: Int) {
  importScan(file: $file, scanId: $scanId) {
    message
  }
}`,O=u`
  mutation RunScan ($scan: OxoAgentScanInputType!) {
    runScan (scan: $scan) {
      scan {
        id
      }
    }
  }
`,v=u`
  mutation ExportScan($scanId: Int!) {
    exportScan(scanId: $scanId) {
      content
    }
  }
`;class q{constructor(t){m(this,"requestor");m(this,"totalScans");this.requestor=new g(t),this.totalScans=0}async getScans(t,a){var n,o,s,c,d;a={...a},a.numberElements===-1&&(a.numberElements=void 0,a.page=void 0);const e=await this.requestor.post(t,{query:N,variables:a}),r=((n=e==null?void 0:e.data)==null?void 0:n.data.scans.scans)||[];return this.totalScans=((d=(c=(s=(o=e==null?void 0:e.data)==null?void 0:o.data)==null?void 0:s.scans)==null?void 0:c.pageInfo)==null?void 0:d.count)||r.length,r}async getScan(t,a){var r,n;const e=await this.requestor.post(t,{query:$,variables:{scanId:a}});return((n=(r=e==null?void 0:e.data)==null?void 0:r.data)==null?void 0:n.scan)||{}}async stopScan(t,a){var r,n;const e=await this.requestor.post(t,{query:E,variables:{scanId:a}});return((n=(r=e==null?void 0:e.data)==null?void 0:r.stopScan)==null?void 0:n.result)||!1}async deleteScan(t,a){var r,n;const e=await this.requestor.post(t,{query:C,variables:{scanId:a}});return((n=(r=e==null?void 0:e.data)==null?void 0:r.deleteScan)==null?void 0:n.result)||!1}async exportScan(t,a){var o,s;const e=await this.requestor.$axios.post(t.endpoint,{query:v,variables:{scanId:a}},{responseType:"arraybuffer",headers:{Accept:"application/ubjson","X-Api-Key":t.apiKey}}),r=b(e==null?void 0:e.data),n=(s=(o=r==null?void 0:r.data)==null?void 0:o.exportScan)==null?void 0:s.content;n!=null&&new T().downloadArrayBuffer("exported_scan.zip",n)}async importScan(t,a,e){var c,d,h,l,p;const r=new FormData,n=x,o={scanId:e,file:null};r.append("operations",JSON.stringify({query:n,variables:o,app:a,maps:{app:["variables.file"]}})),r.append("0",a),r.append("map",JSON.stringify({0:["variables.file"]}));const s=await this.requestor.$axios.post(t.endpoint,r,{headers:{"Content-Type":"multipart/form-data","X-Api-Key":t.apiKey}});if((((c=s==null?void 0:s.data)==null?void 0:c.errors)||[]).length>0)throw new Error((h=(d=s==null?void 0:s.data)==null?void 0:d.errors[0])==null?void 0:h.message);return((p=(l=s==null?void 0:s.data)==null?void 0:l.importScan)==null?void 0:p.result)||!1}async runScan(t,a){var r,n,o,s,c,d,h,l,p,y,f;const e=await this.requestor.post(t,{query:O,variables:{scan:a}});if((((r=e==null?void 0:e.data)==null?void 0:r.errors)||[]).length>0)throw new Error((o=(n=e==null?void 0:e.data)==null?void 0:n.errors[0])==null?void 0:o.message);if(((c=(s=e==null?void 0:e.data)==null?void 0:s.data)==null?void 0:c.runScan)===null||((h=(d=e==null?void 0:e.data)==null?void 0:d.data)==null?void 0:h.runScan)===void 0)throw new Error("An error occurred while creating the scan");return(f=(y=(p=(l=e==null?void 0:e.data)==null?void 0:l.data)==null?void 0:p.runScan)==null?void 0:y.scan)==null?void 0:f.id}}export{g as R,q as S,u as g};
