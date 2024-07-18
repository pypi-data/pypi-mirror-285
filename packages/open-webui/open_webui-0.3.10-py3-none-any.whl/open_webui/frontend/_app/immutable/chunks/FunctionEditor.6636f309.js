import{s as ze,p as _e,f as o,a as T,l as O,g as i,h as c,R as Re,c as A,m as S,d,j as a,i as Ee,r as e,Q as Y,u as ne,O as Qe,n as j,W as Ne,v as Ge,V as Je,P as Ke,w as Xe}from"./scheduler.8ceb707f.js";import{S as Ye,i as Ze,f as Be,b as Ue,d as qe,m as He,a as Le,t as Oe,e as Se}from"./index.07e72a31.js";import{g as $e}from"./navigation.0b220c4f.js";import{C as et}from"./CodeEditor.55f2feeb.js";import{C as tt}from"./ConfirmDialog.beed6fd0.js";function st(t){let u,l,_,V=t[8].t("Please carefully review the following warnings:")+"",v,b,k,D,y=t[8].t("Functions allow arbitrary code execution.")+"",w,I,F,m=t[8].t("Do not install functions from sources you do not fully trust.")+"",p,P,h,M=t[8].t("I acknowledge that I have read and I understand the implications of my action. I am aware of the risks associated with executing arbitrary code and I have verified the trustworthiness of the source.")+"",q;return{c(){u=o("div"),l=o("div"),_=o("div"),v=O(V),b=T(),k=o("ul"),D=o("li"),w=O(y),I=T(),F=o("li"),p=O(m),P=T(),h=o("div"),q=O(M),this.h()},l(r){u=i(r,"DIV",{class:!0});var g=c(u);l=i(g,"DIV",{class:!0});var H=c(l);_=i(H,"DIV",{});var E=c(_);v=S(E,V),E.forEach(d),b=A(H),k=i(H,"UL",{class:!0});var B=c(k);D=i(B,"LI",{});var W=c(D);w=S(W,y),W.forEach(d),I=A(B),F=i(B,"LI",{});var U=c(F);p=S(U,m),U.forEach(d),B.forEach(d),H.forEach(d),P=A(g),h=i(g,"DIV",{class:!0});var x=c(h);q=S(x,M),x.forEach(d),g.forEach(d),this.h()},h(){a(k,"class","mt-1 list-disc pl-4 text-xs"),a(l,"class","bg-yellow-500/20 text-yellow-700 dark:text-yellow-200 rounded-lg px-4 py-3"),a(h,"class","my-3"),a(u,"class","text-sm text-gray-500")},m(r,g){Ee(r,u,g),e(u,l),e(l,_),e(_,v),e(l,b),e(l,k),e(k,D),e(D,w),e(k,I),e(k,F),e(F,p),e(u,P),e(u,h),e(h,q)},p(r,g){g&256&&V!==(V=r[8].t("Please carefully review the following warnings:")+"")&&j(v,V),g&256&&y!==(y=r[8].t("Functions allow arbitrary code execution.")+"")&&j(w,y),g&256&&m!==(m=r[8].t("Do not install functions from sources you do not fully trust.")+"")&&j(p,m),g&256&&M!==(M=r[8].t("I acknowledge that I have read and I understand the implications of my action. I am aware of the risks associated with executing arbitrary code and I have verified the trustworthiness of the source.")+"")&&j(q,M)},d(r){r&&d(u)}}}function lt(t){let u,l,_,V,v,b,k='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4"><path fill-rule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clip-rule="evenodd"></path></svg>',D,y,w=t[8].t("Back")+"",I,F,m,p,P,h,M,q,r,g,H,E,B,W,U,x,Z,$,n,G,N,J,ee=t[8].t("Warning:")+"",oe,pe,te=t[8].t("Functions allow arbitrary code execution")+"",ie,ve,ge,be,K,se=t[8].t("don't install random functions from sources you don't trust.")+"",re,ye,Q,le=t[8].t("Save")+"",ue,de,L,we,C,Ie,ke;function je(s){t[17](s)}let xe={boilerplate:t[10]};t[3]!==void 0&&(xe.value=t[3]),x=new et({props:xe}),_e.push(()=>Be(x,"value",je)),t[18](x),x.$on("save",t[19]);function We(s){t[22](s)}let De={$$slots:{default:[st]},$$scope:{ctx:t}};return t[6]!==void 0&&(De.show=t[6]),L=new tt({props:De}),_e.push(()=>Be(L,"show",We)),L.$on("confirm",t[23]),{c(){u=o("div"),l=o("div"),_=o("form"),V=o("div"),v=o("button"),b=o("div"),b.innerHTML=k,D=T(),y=o("div"),I=O(w),F=T(),m=o("div"),p=o("div"),P=o("div"),h=o("input"),q=T(),r=o("input"),H=T(),E=o("input"),W=T(),U=o("div"),Ue(x.$$.fragment),$=T(),n=o("div"),G=o("div"),N=o("div"),J=o("span"),oe=O(ee),pe=T(),ie=O(te),ve=T(),ge=o("br"),be=O(`—
							`),K=o("span"),re=O(se),ye=T(),Q=o("button"),ue=O(le),de=T(),Ue(L.$$.fragment),this.h()},l(s){u=i(s,"DIV",{class:!0});var f=c(u);l=i(f,"DIV",{class:!0});var ae=c(l);_=i(ae,"FORM",{class:!0});var z=c(_);V=i(z,"DIV",{class:!0});var Fe=c(V);v=i(Fe,"BUTTON",{class:!0,type:!0});var fe=c(v);b=i(fe,"DIV",{class:!0,"data-svelte-h":!0}),Re(b)!=="svelte-1t52rj4"&&(b.innerHTML=k),D=A(fe),y=i(fe,"DIV",{class:!0});var Ve=c(y);I=S(Ve,w),Ve.forEach(d),fe.forEach(d),Fe.forEach(d),F=A(z),m=i(z,"DIV",{class:!0});var X=c(m);p=i(X,"DIV",{class:!0});var ce=c(p);P=i(ce,"DIV",{class:!0});var me=c(P);h=i(me,"INPUT",{class:!0,type:!0,placeholder:!0}),q=A(me),r=i(me,"INPUT",{class:!0,type:!0,placeholder:!0}),me.forEach(d),H=A(ce),E=i(ce,"INPUT",{class:!0,type:!0,placeholder:!0}),ce.forEach(d),W=A(X),U=i(X,"DIV",{class:!0});var Pe=c(U);qe(x.$$.fragment,Pe),Pe.forEach(d),$=A(X),n=i(X,"DIV",{class:!0});var he=c(n);G=i(he,"DIV",{class:!0});var Me=c(G);N=i(Me,"DIV",{class:!0});var R=c(N);J=i(R,"SPAN",{class:!0});var Ce=c(J);oe=S(Ce,ee),Ce.forEach(d),pe=A(R),ie=S(R,te),ve=A(R),ge=i(R,"BR",{}),be=S(R,`—
							`),K=i(R,"SPAN",{class:!0});var Te=c(K);re=S(Te,se),Te.forEach(d),R.forEach(d),Me.forEach(d),ye=A(he),Q=i(he,"BUTTON",{class:!0,type:!0});var Ae=c(Q);ue=S(Ae,le),Ae.forEach(d),he.forEach(d),X.forEach(d),z.forEach(d),ae.forEach(d),f.forEach(d),de=A(s),qe(L.$$.fragment,s),this.h()},h(){a(b,"class","self-center"),a(y,"class","self-center font-medium text-sm"),a(v,"class","flex space-x-1"),a(v,"type","button"),a(V,"class","mb-2.5"),a(h,"class","w-full px-3 py-2 text-sm font-medium bg-gray-50 dark:bg-gray-850 dark:text-gray-200 rounded-lg outline-none"),a(h,"type","text"),a(h,"placeholder",M=t[8].t("Function Name (e.g. My Filter)")),h.required=!0,a(r,"class","w-full px-3 py-2 text-sm font-medium disabled:text-gray-300 dark:disabled:text-gray-700 bg-gray-50 dark:bg-gray-850 dark:text-gray-200 rounded-lg outline-none"),a(r,"type","text"),a(r,"placeholder",g=t[8].t("Function ID (e.g. my_filter)")),r.required=!0,r.disabled=t[4],a(P,"class","flex gap-2 w-full"),a(E,"class","w-full px-3 py-2 text-sm font-medium bg-gray-50 dark:bg-gray-850 dark:text-gray-200 rounded-lg outline-none"),a(E,"type","text"),a(E,"placeholder",B=t[8].t("Function Description (e.g. A filter to remove profanity from text)")),E.required=!0,a(p,"class","w-full mb-2 flex flex-col gap-1.5"),a(U,"class","mb-2 flex-1 overflow-auto h-0 rounded-lg"),a(J,"class","font-semibold dark:text-gray-200"),a(K,"class","font-medium dark:text-gray-400"),a(N,"class","text-xs text-gray-500 line-clamp-2"),a(G,"class","flex-1 pr-3"),a(Q,"class","px-3 py-1.5 text-sm font-medium bg-emerald-600 hover:bg-emerald-700 text-gray-50 transition rounded-lg"),a(Q,"type","submit"),a(n,"class","pb-3 flex justify-between"),a(m,"class","flex flex-col flex-1 overflow-auto h-0 rounded-lg"),a(_,"class","flex flex-col max-h-[100dvh] h-full"),a(l,"class","mx-auto w-full md:px-0 h-full"),a(u,"class","flex flex-col justify-between w-full overflow-y-auto h-full")},m(s,f){Ee(s,u,f),e(u,l),e(l,_),e(_,V),e(V,v),e(v,b),e(v,D),e(v,y),e(y,I),e(_,F),e(_,m),e(m,p),e(p,P),e(P,h),Y(h,t[0]),e(P,q),e(P,r),Y(r,t[1]),e(p,H),e(p,E),Y(E,t[2].description),e(m,W),e(m,U),He(x,U,null),e(m,$),e(m,n),e(n,G),e(G,N),e(N,J),e(J,oe),e(N,pe),e(N,ie),e(N,ve),e(N,ge),e(N,be),e(N,K),e(K,re),e(n,ye),e(n,Q),e(Q,ue),t[20](_),Ee(s,de,f),He(L,s,f),C=!0,Ie||(ke=[ne(v,"click",t[13]),ne(h,"input",t[14]),ne(r,"input",t[15]),ne(E,"input",t[16]),ne(_,"submit",Qe(t[21]))],Ie=!0)},p(s,[f]){(!C||f&256)&&w!==(w=s[8].t("Back")+"")&&j(I,w),(!C||f&256&&M!==(M=s[8].t("Function Name (e.g. My Filter)")))&&a(h,"placeholder",M),f&1&&h.value!==s[0]&&Y(h,s[0]),(!C||f&256&&g!==(g=s[8].t("Function ID (e.g. my_filter)")))&&a(r,"placeholder",g),(!C||f&16)&&(r.disabled=s[4]),f&2&&r.value!==s[1]&&Y(r,s[1]),(!C||f&256&&B!==(B=s[8].t("Function Description (e.g. A filter to remove profanity from text)")))&&a(E,"placeholder",B),f&4&&E.value!==s[2].description&&Y(E,s[2].description);const ae={};!Z&&f&8&&(Z=!0,ae.value=s[3],Ne(()=>Z=!1)),x.$set(ae),(!C||f&256)&&ee!==(ee=s[8].t("Warning:")+"")&&j(oe,ee),(!C||f&256)&&te!==(te=s[8].t("Functions allow arbitrary code execution")+"")&&j(ie,te),(!C||f&256)&&se!==(se=s[8].t("don't install random functions from sources you don't trust.")+"")&&j(re,se),(!C||f&256)&&le!==(le=s[8].t("Save")+"")&&j(ue,le);const z={};f&268435712&&(z.$$scope={dirty:f,ctx:s}),!we&&f&64&&(we=!0,z.show=s[6],Ne(()=>we=!1)),L.$set(z)},i(s){C||(Le(x.$$.fragment,s),Le(L.$$.fragment,s),C=!0)},o(s){Oe(x.$$.fragment,s),Oe(L.$$.fragment,s),C=!1},d(s){s&&(d(u),d(de)),t[18](null),Se(x),t[20](null),Se(L,s),Ie=!1,Ge(ke)}}}function at(t,u,l){let _;const V=Je(),v=Ke("i18n");Xe(t,v,n=>l(8,_=n));let b=null,k=!1,{edit:D=!1}=u,{clone:y=!1}=u,{id:w=""}=u,{name:I=""}=u,{meta:F={description:""}}=u,{content:m=""}=u,p,P=`"""
title: Example Filter
author: open-webui
author_url: https://github.com/open-webui
funding_url: https://github.com/open-webui
version: 0.1
"""

from pydantic import BaseModel, Field
from typing import Optional


class Filter:
    class Valves(BaseModel):
        priority: int = Field(
            default=0, description="Priority level for the filter operations."
        )
        max_turns: int = Field(
            default=8, description="Maximum allowable conversation turns for a user."
        )
        pass

    class UserValves(BaseModel):
        max_turns: int = Field(
            default=4, description="Maximum allowable conversation turns for a user."
        )
        pass

    def __init__(self):
        # Indicates custom file handling logic. This flag helps disengage default routines in favor of custom
        # implementations, informing the WebUI to defer file-related operations to designated methods within this class.
        # Alternatively, you can remove the files directly from the body in from the inlet hook
        # self.file_handler = True

        # Initialize 'valves' with specific configurations. Using 'Valves' instance helps encapsulate settings,
        # which ensures settings are managed cohesively and not confused with operational flags like 'file_handler'.
        self.valves = self.Valves()
        pass

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Modify the request body or validate it before processing by the chat completion API.
        # This function is the pre-processor for the API where various checks on the input can be performed.
        # It can also modify the request before sending it to the API.
        print(f"inlet:{__name__}")
        print(f"inlet:body:{body}")
        print(f"inlet:user:{__user__}")

        if __user__.get("role", "admin") in ["user", "admin"]:
            messages = body.get("messages", [])

            max_turns = min(__user__["valves"].max_turns, self.valves.max_turns)
            if len(messages) > max_turns:
                raise Exception(
                    f"Conversation turn limit exceeded. Max turns: {max_turns}"
                )

        return body

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        # Modify or analyze the response body after processing by the API.
        # This function is the post-processor for the API, which can be used to modify the response
        # or perform additional checks and analytics.
        print(f"outlet:{__name__}")
        print(f"outlet:body:{body}")
        print(f"outlet:user:{__user__}")

        return body
`;const h=async()=>{V("save",{id:w,name:I,meta:F,content:m})},M=async()=>{p&&await p.formatPythonCodeHandler()&&(console.log("Code formatted successfully"),h())},q=()=>{$e("/workspace/functions")};function r(){I=this.value,l(0,I)}function g(){w=this.value,l(1,w),l(0,I),l(4,D),l(12,y)}function H(){F.description=this.value,l(2,F)}function E(n){m=n,l(3,m)}function B(n){_e[n?"unshift":"push"](()=>{p=n,l(7,p)})}const W=()=>{b&&b.requestSubmit()};function U(n){_e[n?"unshift":"push"](()=>{b=n,l(5,b)})}const x=()=>{D?M():l(6,k=!0)};function Z(n){k=n,l(6,k)}const $=()=>{M()};return t.$$set=n=>{"edit"in n&&l(4,D=n.edit),"clone"in n&&l(12,y=n.clone),"id"in n&&l(1,w=n.id),"name"in n&&l(0,I=n.name),"meta"in n&&l(2,F=n.meta),"content"in n&&l(3,m=n.content)},t.$$.update=()=>{t.$$.dirty&4113&&I&&!D&&!y&&l(1,w=I.replace(/\s+/g,"_").toLowerCase())},[I,w,F,m,D,b,k,p,_,v,P,M,y,q,r,g,H,E,B,W,U,x,Z,$]}class dt extends Ye{constructor(u){super(),Ze(this,u,at,lt,ze,{edit:4,clone:12,id:1,name:0,meta:2,content:3})}}export{dt as F};
//# sourceMappingURL=FunctionEditor.6636f309.js.map
