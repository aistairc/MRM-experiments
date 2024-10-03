import torch
import torch.nn as nn
import torch.nn.functional as F
from .Model import Model

def load_file(filepath):
  with open(filepath) as fp:
      _ = fp.readline() # skip first line (number of data)
      import csv
      reader = csv.reader(fp, delimiter='\t')
      return dict(list(reader))

def switch_kv(data: dict):
    assert len(data.keys()) == len(set(list(data.values())))
    return {v:k for k, v in data.items()}

class TransU(Model):

        def __init__(self, ent_tot, rel_tot, id_to_entity, id_to_relation, uri_to_embeddings, 
                dim = 100, p_norm = 1, norm_flag = True, margin = None, epsilon = None):
                super(TransU, self).__init__(ent_tot, rel_tot)
                
                self.dim = dim
                self.margin = margin
                self.epsilon = epsilon
                self.norm_flag = norm_flag
                self.p_norm = p_norm
                
                original_ent_map = id_to_entity   # id to uri
                original_rel_map = id_to_relation # id to uri
                
                uris = list(uri_to_embeddings.keys()) + list(original_ent_map.values()) + list(original_rel_map.values())
                uris = sorted(list(set(uris)))
                print('[#URIs]', len(uris))
                uris_to_id = switch_kv(dict(enumerate(uris)))
                embeddings = []
                counts = 0
                for uri, _id in uris_to_id.items():
                    if uri not in uri_to_embeddings.keys():
                        vec = torch.randn(dim)
                    else:
                        vec = uri_to_embeddings[uri]
                        counts += 1
                    embeddings.append(vec)
                embeddings = torch.stack(embeddings)
                print(f'[EMBEDDINGS MATCHED]: {counts / len(uris_to_id) * 100:.2f}')
                
                self.org_id_to_transu_id_for_rel = dict()
                self.org_id_to_transu_id_for_ent = dict()

                for k, v in original_ent_map.items():
                    self.org_id_to_transu_id_for_ent[k] = uris_to_id[v]
                
                for k, v in original_rel_map.items():
                    self.org_id_to_transu_id_for_rel[k] = uris_to_id[v]
                
                self.ent_embeddings = nn.Embedding(len(uris), self.dim)
                self.ent_embeddings.weight.data = embeddings.to(self.ent_embeddings.weight.data.device).to(self.ent_embeddings.weight.data.dtype)
                # print(self.ent_embeddings.weight.data.shape)
                # self.rel_embeddings = nn.Embedding(len(uris), self.dim)

                for e_id, e_uri in original_ent_map.items():
                    for r_id, r_uri in original_rel_map.items():
                        if e_uri == r_uri:
                            assert self.org_id_to_transu_id_for_ent[e_id] == self.org_id_to_transu_id_for_rel[r_id]
                        else:
                            assert self.org_id_to_transu_id_for_ent[e_id] != self.org_id_to_transu_id_for_rel[r_id]


                if margin == None or epsilon == None:
                        nn.init.xavier_uniform_(self.ent_embeddings.weight.data)
                        # nn.init.xavier_uniform_(self.rel_embeddings.weight.data)
                else:
                        self.embedding_range = nn.Parameter(
                                torch.Tensor([(self.margin + self.epsilon) / self.dim]), requires_grad=False
                        )
                        nn.init.uniform_(
                                tensor = self.ent_embeddings.weight.data, 
                                a = -self.embedding_range.item(), 
                                b = self.embedding_range.item()
                        )
                        # nn.init.uniform_(
                        #         tensor = self.rel_embeddings.weight.data, 
                        #         a= -self.embedding_range.item(), 
                        #         b= self.embedding_range.item()
                        # )

                if margin != None:
                        self.margin = nn.Parameter(torch.Tensor([margin]))
                        self.margin.requires_grad = False
                        self.margin_flag = True
                else:
                        self.margin_flag = False



        @property
        def rel_embeddings(self):
            return self.ent_embeddings

        def apply_map(self, ids, mode='ent'):
            if   mode == 'ent':
                org_id_to_transu_id = self.org_id_to_transu_id_for_ent
            elif mode == 'rel':
                org_id_to_transu_id = self.org_id_to_transu_id_for_rel
            else:
                raise
            input_ids = [org_id_to_transu_id[int(i)] for i in ids]

            if isinstance(ids, torch.Tensor):
                return torch.tensor(input_ids, device=ids.device, dtype=ids.dtype)
            elif isinstance(ids, list):
                return input_ids
            else:
                raise

        def _calc(self, h, t, r, mode):
                if self.norm_flag:
                        h = F.normalize(h, 2, -1)
                        r = F.normalize(r, 2, -1)
                        t = F.normalize(t, 2, -1)
                if mode != 'normal':
                        h = h.view(-1, r.shape[0], h.shape[-1])
                        t = t.view(-1, r.shape[0], t.shape[-1])
                        r = r.view(-1, r.shape[0], r.shape[-1])
                if mode == 'head_batch':
                        score = h + (r - t)
                else:
                        score = (h + r) - t
                score = torch.norm(score, self.p_norm, -1).flatten()
                return score

        def forward(self, data):
                batch_h = data['batch_h']
                batch_t = data['batch_t']
                batch_r = data['batch_r']
                batch_h = self.apply_map(batch_h, 'ent')
                batch_t = self.apply_map(batch_t, 'ent')
                batch_r = self.apply_map(batch_r, 'rel')

                # print("batch_h", batch_h.max(), batch_h.min(), self.ent_embeddings, self.ent_embeddings.weight.data.shape)
                # print("batch_r", batch_r.max(), batch_r.min(), self.rel_embeddings)
                # print("batch_t", batch_t.max(), batch_t.min())

                mode = data['mode']
                h = self.ent_embeddings(batch_h)
                # print("h", h)
                t = self.ent_embeddings(batch_t)
                # print("t", t)
                r = self.rel_embeddings(batch_r)
                # print("r", r)
                score = self._calc(h ,t, r, mode)
                if self.margin_flag:
                        return self.margin - score
                else:
                        return score

        def regularization(self, data):
                batch_h = data['batch_h']
                batch_t = data['batch_t']
                batch_r = data['batch_r']
                batch_h = self.apply_map(batch_h, 'ent')
                batch_t = self.apply_map(batch_t, 'ent')
                batch_r = self.apply_map(batch_r, 'rel')
                
                h = self.ent_embeddings(batch_h)
                t = self.ent_embeddings(batch_t)
                r = self.rel_embeddings(batch_r)
                regul = (torch.mean(h ** 2) + 
                                 torch.mean(t ** 2) + 
                                 torch.mean(r ** 2)) / 3
                return regul

        def predict(self, data):
                score = self.forward(data)
                if self.margin_flag:
                        score = self.margin - score
                        return score.cpu().data.numpy()
                else:
                        return score.cpu().data.numpy()
