from cwmaya.template.smoke import cw_smoke_template
from cwmaya.template.sim_render import cw_sim_render_template
from cwmaya.template.chain import cw_chain_template

TEMPLATES = {
    "cwSmokeSubmission": cw_smoke_template.CwSmokeTemplate,
    "cwSimRenderSubmission": cw_sim_render_template.CwSimRenderTemplate,
    "cwChainSubmission": cw_chain_template.CwChainTemplate,
}
