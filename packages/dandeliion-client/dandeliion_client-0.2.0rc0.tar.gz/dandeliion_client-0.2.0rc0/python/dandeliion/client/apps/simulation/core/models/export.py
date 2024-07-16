import importlib
import json
from dandeliion.client.tools.misc import flatten_dict, unflatten_dict


class BPX:

    @staticmethod
    def export(meta, params, version=None, raw=True):
        model = meta['model']
        params = flatten_dict(params)
        model_class = getattr(importlib.import_module('dandeliion.client.apps.simulation.core.models'),
                              model)
        if not version:
            version = model_class.Meta.exports['bpx']['default']
        BPXConverter = model_class.Meta.exports['bpx']['version'][version]

        bpx_out = BPXConverter.export(params=params, meta=meta)

        if raw:
            return 'application/bpx', json.dumps(bpx_out, ensure_ascii=False, indent=4)
        return bpx_out

    @staticmethod
    def import_(data, model=None, version=None):

        version_ = data['Header']['BPX']
        if version and version_ != version:
            raise ValueError(f'Version of data does not match requested version: {version} != {version_}')
        if not model:
            model = 'Battery_Pouch_1D'  # TODO should be determined by 'model'
        model_class = getattr(importlib.import_module('dandeliion.client.apps.simulation.core.models'),
                              model)
        BPXConverter = model_class.Meta.exports['bpx']['version'][version_]
        return unflatten_dict(BPXConverter.import_(data))
