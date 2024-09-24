import re
import random
import math
from collections import Counter, defaultdict
from text_utils import normalize_text


class SpellChecker:
    """
    A context-sensitive spell checker based on the Noisy Channel model.

    This class implements a spell-checker using a combination of a language model
    and error distribution model to identify and correct spelling errors in text.
    The corrections are based on probabilistic analysis of potential edit distances
    between the observed tokens and their potential correct forms.
    """

    def __init__(self, lm=None, error_tables=None):
        """
        Initialize the SpellChecker instance with a given language model and error tables.

        Parameters:
        -----------
        lm : LanguageModel, optional
            A language model object that provides probabilities of tokens in the text (default is None).
        error_tables : dict, optional
            A dictionary containing error tables for common spelling mistakes. This includes:
            - Insertion errors
            - Deletion errors
            - Substitution errors
            - Transposition errors
            If not provided, a default set of error tables is used.
        """
        self.lm = lm
        self.possible_edits = {}  # Dictionary to store possible corrections and their probabilities - {candidate: probability}
        self.error_tables = error_tables
        if self.error_tables == None:
            self.error_tables = {'insertion': {'gw': 1, 'gv': 0, 'gu': 3, 'gt': 2, 'gs': 69, 'gr': 5, 'gq': 1, 'gp': 0, '#y': 1, 'gz': 0, 'gy': 0, 'gx': 0, 'gg': 5, 'gf': 1, 'ge': 5, 'gd': 0, 'gc': 0, 'gb': 0, 'ga': 8, 'go': 1, 'gn': 1, 'gm': 0, 'gl': 2, 'gk': 0, 'gj': 0, 'gi': 8, 'gh': 12, 'tz': 0, 'tx': 0, 'ty': 6, 'tv': 0, 'tw': 5, 'tt': 183, 'tu': 11, 'tr': 54, 'ts': 264, 'tp': 1, 'tq': 0, 'tn': 1, 'to': 23, 'tl': 6, 'tm': 3, 'tj': 1, 'tk': 0, 'th': 24, 'ti': 59, 'tf': 1, 'tg': 10, 'td': 3, 'te': 65, 'tb': 0, 'tc': 0, 'ta': 39, 'vu': 1, 'zl': 0, 'zm': 0, 'zn': 0, 'zo': 0, 'zh': 0, 'zi': 6, 'zj': 0, 'zk': 0, 'zd': 0, 'ze': 5, 'zf': 1, 'zg': 0, 'za': 2, 'zb': 0, 'zc': 0, 'zx': 0, 'zy': 2, 'zz': 4, 'zt': 0, 'zu': 0, 'zv': 0, 'zw': 0, 'zp': 0, 'zq': 0, 'zr': 0, 'zs': 0, '#s': 23, 'wl': 1, '#q': 0, 'va': 0, '#c': 9, 'vc': 0, 'wk': 1, '#p': 10, 'vh': 0, 'wj': 0, 'vi': 10, 'vj': 0, 'vk': 0, 'vl': 1, 'vm': 0, 'wi': 1, '#v': 1, 'vn': 1, 'vo': 0, 'me': 17, 'md': 0, 'mg': 0, 'mf': 0, 'ma': 11, 'mc': 1, 'mb': 1, 'mm': 102, 'ml': 0, 'mo': 7, 'mn': 44, 'mi': 6, 'mh': 1, 'mk': 1, 'mj': 0, 'mu': 2, 'mt': 1, 'mw': 1, 'mv': 0, 'mq': 0, 'mp': 2, 'ms': 47, 'mr': 0, 'vt': 0, 'my': 0, 'mx': 0, 'mz': 0, 'vv': 5, 'vw': 1, '#t': 2, 'vx': 0, 'vz': 0, '#b': 8, 'fp': 0, 'fq': 0, 'fr': 5, 'fs': 23, 'ft': 0, 'fu': 1, 'fv': 0, 'fw': 0, 'fx': 0, 'fy': 1, 'fz': 0, 'fa': 1, 'fb': 0, 'fc': 0, 'fd': 0, 'fe': 2, 'ff': 27, 'fg': 1, 'fh': 0, 'fi': 12, 'fj': 0, 'fk': 0, 'fl': 10, 'fm': 0, 'fn': 0, 'fo': 0, 'sz': 0, 'sy': 7, 'sx': 0, 'ss': 205, 'sr': 1, 'sq': 0, 'sp': 1, 'sw': 1, 'sv': 0, 'su': 7, 'st': 49, 'sk': 2, 'sj': 0, 'si': 101, 'sh': 50, 'so': 3, 'sn': 7, 'sm': 10, 'sl': 2, 'sc': 7, 'sb': 1, 'sa': 13, 'sg': 1, 'sf': 0, 'se': 41, 'sd': 20, 'lf': 0, 'lg': 0, 'ld': 1, 'le': 38, 'lb': 1, 'lc': 0, 'la': 3, 'ln': 0, 'lo': 7, 'll': 128, 'lm': 1, 'lj': 0, 'lk': 2, 'lh': 0, 'li': 79, 'lv': 1, 'lw': 0, 'lt': 7, 'lu': 3, 'lr': 0, 'ls': 97, 'lp': 0, 'lq': 0, 'lz': 0, 'lx': 0, 'ly': 2, 'wq': 1, 'yh': 0, 'yk': 0, 'yj': 0, 'ym': 1, 'yl': 1, 'yo': 0, 'yn': 6, 'ya': 5, 'yc': 2, 'yb': 1, 'ye': 3, 'yd': 0, 'yg': 0, 'yf': 0, 'yy': 2, 'yx': 0, 'yz': 0, 'yq': 0, 'yp': 0, 'ys': 33, 'yr': 1, 'yu': 13, 'yt': 1, 'yw': 1, 'yv': 0, 'em': 6, 'el': 4, 'eo': 5, 'en': 27, 'ei': 4, 'eh': 1, 'ek': 3, 'ej': 0, 'ee': 147, 'ed': 76, 'eg': 0, 'ef': 2, 'ea': 39, 'ec': 8, 'eb': 2, 'ey': 8, 'ex': 2, '#g': 14, 'ez': 0, 'eu': 4, 'et': 6, 'ew': 10, 'ev': 1, 'eq': 0, 'ep': 1, 'es': 417, 'er': 83, 'rt': 29, 'ru': 7, 'rv': 0, 'rw': 1, 'rp': 0, 'rq': 0, 'rr': 132, 'rs': 273, 'rx': 0, 'ry': 10, 'rz': 0, 'rd': 0, 're': 89, 'rf': 1, 'rg': 1, 'ra': 15, 'rb': 2, 'rc': 1, 'rl': 5, 'rm': 9, 'rn': 7, 'ro': 10, 'rh': 2, 'ri': 64, 'rj': 0, 'rk': 0, 'xj': 0, 'xk': 0, 'xh': 6, 'xi': 1, 'xn': 0, 'xo': 3, 'xl': 0, 'xm': 1, 'xb': 0, 'xc': 18, 'xa': 0, 'xf': 0, 'xg': 0, 'xd': 0, 'xe': 1, 'xz': 0, 'xx': 1, 'xy': 0, 'xr': 0, 'xs': 2, 'xp': 0, 'xq': 0, 'xv': 0, 'xw': 0, 'xt': 0, 'xu': 0, 'wy': 0, 'wx': 0, '#d': 8, 'kc': 0, 'kb': 4, 'ka': 2, 'kg': 0, 'kf': 0, 'ke': 9, 'kd': 1, 'kk': 1, 'kj': 0, 'ki': 1, 'kh': 1, 'ko': 2, 'kn': 0, 'km': 0, 'kl': 1, 'ks': 95, 'kr': 0, 'kq': 0, 'kp': 1, 'kw': 0, 'kv': 0, 'ku': 1, 'kt': 0, 'kz': 0, 'ky': 4, 'kx': 0, 'dn': 9, 'do': 13, 'dl': 6, 'dm': 1, 'dj': 0, 'dk': 0, 'dh': 0, 'di': 9, 'df': 2, 'dg': 0, 'dd': 17, 'de': 14, 'db': 0, 'dc': 3, 'da': 18, 'dz': 0, 'dx': 0, 'dy': 5, 'dv': 0, 'dw': 0, 'dt': 0, 'du': 0, 'dr': 6, 'ds': 119, 'dp': 0, 'dq': 0, 'qq': 0, 'qp': 0, 'qs': 0, 'qr': 0, 'qu': 1, 'qt': 0, 'qw': 0, 'qv': 0, 'qy': 0, 'qx': 0, 'qz': 0, 'qa': 0, 'qc': 0, 'qb': 0, 'qe': 0, 'qd': 0, 'qg': 0, 'qf': 0, 'qi': 1, 'qh': 0, 'qk': 0, 'qj': 0, 'qm': 0, 'ql': 0, 'qo': 0, 'qn': 0, '#k': 17, '#j': 1, '#e': 26, '#i': 5, '#h': 3, 'wc': 0, 'wb': 0, 'wa': 0, 'wo': 0, 'wn': 2, 'wm': 0, 'wg': 0, 'wf': 0, 'we': 10, 'wd': 1, 'jx': 0, 'jy': 0, 'jz': 0, '#l': 5, 'jt': 0, 'ju': 1, 'jv': 0, 'jw': 0, 'jp': 0, 'jq': 0, 'jr': 0, 'js': 0, 'jl': 0, 'jm': 0, 'jn': 0, 'jo': 0, 'jh': 0, 'ji': 0, 'jj': 0, 'jk': 0, 'jd': 0, 'je': 0, 'jf': 0, 'jg': 0, '#w': 2, 'ja': 0, 'jb': 0, 'jc': 0, 'ww': 4, 'wv': 0, 'wu': 2, 'wt': 0, 'ws': 8, 'wr': 1, 'ck': 3, 'cj': 0, 'ci': 50, 'ch': 18, 'co': 7, 'cn': 1, 'cm': 1, 'cl': 1, 'cc': 54, 'cb': 0, 'ca': 19, 'wp': 0, 'cg': 0, 'cf': 0, 'ce': 13, 'cd': 1, 'cz': 0, 'cy': 0, 'cx': 1, '#r': 6, 'cs': 25, 'cr': 7, 'cq': 0, 'cp': 1, 'cw': 0, 'cv': 4, 'cu': 8, 'ct': 7, 'pr': 29, 'ps': 52, 'pp': 70, 'pq': 0, 'pv': 1, 'pw': 1, 'pt': 9, 'pu': 1, 'pz': 0, 'px': 0, 'py': 0, 'wz': 0, 'pb': 0, 'pc': 1, 'pa': 23, 'pf': 0, 'pg': 0, 'pd': 1, 'pe': 10, 'pj': 0, 'pk': 0, 'ph': 20, 'pi': 3, 'pn': 0, 'po': 26, 'pl': 2, 'pm': 0, 'iy': 0, 'ix': 1, 'vb': 2, 'iz': 1, 'vd': 0, 've': 36, 'vf': 0, 'vg': 0, 'iq': 0, 'ip': 1, 'is': 30, 'ir': 9, 'iu': 11, 'it': 29, 'iw': 0, 'iv': 0, 'ii': 69, 'ih': 1, 'ik': 1, 'ij': 2, 'im': 11, 'il': 17, 'io': 27, 'in': 33, 'ia': 10, 'vy': 0, 'ic': 13, 'ib': 3, 'ie': 25, 'id': 13, 'ig': 1, 'if': 0, '#x': 1, 'wh': 1, 'yi': 2, '#u': 11, 'vr': 0, '#f': 11, '#o': 2, '#n': 2, '#m': 6, 'vs': 0, 'bd': 0, 'be': 7, 'bf': 0, 'bg': 1, 'ba': 3, 'bb': 11, 'bc': 0, 'bl': 15, 'bm': 0, 'bn': 1, 'bo': 1, 'bh': 0, 'bi': 50, 'bj': 0, 'bk': 0, 'bt': 0, 'bu': 0, 'bv': 3, 'bw': 0, 'bp': 0, 'bq': 0, 'br': 5, 'bs': 16, 'bx': 0, 'by': 0, 'bz': 0, 'oo': 64, 'on': 13, 'om': 3, 'ol': 6, 'ok': 0, 'oj': 1, 'oi': 28, 'oh': 0, 'og': 1, 'of': 2, 'oe': 7, 'od': 3, 'oc': 1, 'ob': 1, 'oa': 14, 'oz': 1, 'oy': 1, 'ox': 0, 'ow': 0, 'ov': 1, 'ou': 19, 'ot': 4, 'os': 59, 'or': 16, 'oq': 0, 'op': 30, '#a': 46, 'hz': 0, 'hx': 0, 'hy': 3, 'hr': 16, 'hs': 24, 'hp': 0, 'hq': 0, 'hv': 0, 'hw': 5, 'ht': 22, 'hu': 1, 'hj': 2, 'hk': 0, 'hh': 18, 'hi': 17, 'hn': 1, 'ho': 4, 'hl': 1, 'hm': 0, 'hb': 1, 'hc': 0, 'ha': 4, 'hf': 0, 'hg': 10, 'hd': 1, 'he': 24, 'uy': 3, 'ux': 2, 'uz': 0, 'uu': 26, 'ut': 27, 'uw': 0, 'uv': 0, 'uq': 0, 'up': 3, 'us': 19, 'ur': 49, 'um': 3, 'ul': 3, 'uo': 1, 'un': 9, 'ui': 24, 'uh': 1, 'uk': 1, 'uj': 1, 'ue': 9, 'ud': 0, 'ug': 0, 'uf': 0, 'ua': 15, 'uc': 3, 'ub': 0, 'aa': 15, 'ac': 14, 'ab': 1, 'ae': 10, 'ad': 7, 'ag': 1, 'af': 0, 'ai': 33, 'ah': 1, 'ak': 4, 'aj': 1, 'am': 2, 'al': 31, 'ao': 12, 'an': 39, 'aq': 3, 'ap': 4, 'as': 134, 'ar': 28, 'au': 28, 'at': 7, 'aw': 1, 'av': 0, 'ay': 4, 'ax': 1, 'az': 1, 'nh': 0, 'ni': 34, 'nj': 0, 'nk': 1, 'nl': 1, 'nm': 26, 'nn': 99, 'no': 12, 'na': 15, 'nb': 5, 'nc': 7, 'nd': 13, 'ne': 52, 'nf': 4, 'ng': 17, 'nx': 0, 'ny': 1, 'nz': 0, 'np': 0, 'nq': 0, 'nr': 2, 'ns': 156, 'nt': 53, 'nu': 1, 'nv': 1, 'nw': 0, 'vp': 1, '#z': 2, 'vq': 0},
                                 'deletion': {'tz': 0, 'tx': 0, 'ty': 2, 'tv': 0, 'tw': 4, 'tt': 137, 'tu': 14, 'tr': 203, 'ts': 5, 'tp': 1, 'tq': 0, 'tn': 3, 'to': 11, 'tl': 31, 'tm': 3, 'tj': 0, 'tk': 0, 'th': 49, 'ti': 427, 'tf': 1, 'tg': 7, 'td': 0, 'te': 76, 'tb': 1, 'tc': 2, 'ta': 24, 'me': 33, 'md': 0, 'mg': 0, 'mf': 0, 'ma': 15, 'mc': 0, 'mb': 10, 'mm': 180, 'ml': 0, 'mo': 7, 'mn': 7, 'mi': 42, 'mh': 1, 'mk': 0, 'mj': 0, 'mu': 4, 'mt': 0, 'mw': 0, 'mv': 0, 'mq': 0, 'mp': 31, 'ms': 9, 'mr': 0, 'my': 0, 'mx': 0, 'mz': 0, 'fp': 0, 'fq': 0, 'fr': 11, 'fs': 0, 'ft': 8, 'fu': 1, 'fv': 0, 'fw': 0, 'fx': 0, 'fy': 1, 'fz': 0, 'fa': 4, 'fb': 0, 'fc': 0, 'fd': 0, 'fe': 13, 'ff': 46, 'fg': 0, 'fh': 0, 'fi': 79, 'fj': 0, 'fk': 0, 'fl': 12, 'fm': 0, 'fn': 0, 'fo': 4, 'yi': 1, 'yh': 0, 'yk': 0, 'yj': 0, 'ym': 2, 'yl': 1, 'yo': 1, 'yn': 1, 'ya': 2, 'yc': 34, 'yb': 1, 'ye': 2, 'yd': 0, 'yg': 1, 'yf': 0, 'yy': 0, 'yx': 0, 'yz': 0, 'yq': 0, 'yp': 1, 'ys': 17, 'yr': 0, 'yu': 0, 'yt': 1, 'yw': 1, 'yv': 0, 'rt': 68, 'ru': 0, 'rv': 10, 'rw': 1, 'rp': 2, 'rq': 0, 'rr': 277, 'rs': 103, 'rx': 0, 'ry': 27, 'rz': 0, 'rd': 19, 're': 188, 'rf': 0, 'rg': 11, 'ra': 63, 'rb': 4, 'rc': 12, 'rl': 33, 'rm': 7, 'rn': 157, 'ro': 21, 'rh': 5, 'ri': 132, 'rj': 0, 'rk': 3, 'kc': 0, 'kb': 0, 'ka': 4, 'kg': 8, 'kf': 1, 'ke': 15, 'kd': 1, 'kk': 1, 'kj': 0, 'ki': 5, 'kh': 1, 'ko': 0, 'kn': 17, 'km': 0, 'kl': 3, 'ks': 5, 'kr': 1, 'kq': 0, 'kp': 0, 'kw': 1, 'kv': 0, 'ku': 0, 'kt': 0, 'kz': 0, 'ky': 0, 'kx': 0, 'dn': 3, 'do': 3, 'dl': 8, 'dm': 4, 'dj': 1, 'dk': 1, 'dh': 0, 'di': 62, 'df': 0, 'dg': 10, 'dd': 25, 'de': 45, 'db': 0, 'dc': 7, 'da': 12, 'dz': 0, 'dx': 0, 'dy': 6, 'dv': 2, 'dw': 0, 'dt': 0, 'du': 3, 'dr': 11, 'ds': 1, 'dp': 0, 'dq': 0, 'wg': 0, 'wf': 1, 'we': 11, 'wd': 1, 'wc': 0, 'wb': 0, 'wa': 40, 'wo': 2, 'wn': 2, 'wm': 0, 'wl': 1, 'wk': 0, 'wj': 0, 'wi': 15, 'wh': 11, 'ww': 0, 'wv': 0, 'wu': 0, 'wt': 0, 'ws': 24, 'wr': 2, 'wq': 0, 'wp': 0, 'wz': 0, 'wy': 0, 'wx': 0, 'pr': 58, 'ps': 1, 'pp': 93, 'pq': 0, 'pv': 0, 'pw': 0, 'pt': 18, 'pu': 2, 'pz': 0, 'px': 0, 'py': 0, 'pb': 0, 'pc': 0, 'pa': 25, 'pf': 0, 'pg': 0, 'pd': 0, 'pe': 22, 'pj': 0, 'pk': 0, 'ph': 12, 'pi': 15, 'pn': 0, 'po': 30, 'pl': 28, 'pm': 1, 'iy': 1, 'ix': 0, 'iz': 7, 'iq': 0, 'ip': 7, 'is': 71, 'ir': 16, 'iu': 1, 'it': 64, 'iw': 0, 'iv': 1, 'ii': 1, 'ih': 0, 'ik': 0, 'ij': 0, 'im': 14, 'il': 38, 'io': 41, 'in': 82, 'ia': 26, 'ic': 60, 'ib': 1, 'ie': 23, 'id': 26, 'ig': 9, 'if': 1, 'bd': 0, 'be': 22, 'bf': 0, 'bg': 0, 'ba': 2, 'bb': 2, 'bc': 1, 'bl': 26, 'bm': 0, 'bn': 0, 'bo': 2, 'bh': 0, 'bi': 183, 'bj': 0, 'bk': 0, 'bt': 0, 'bu': 6, 'bv': 1, 'bw': 0, 'bp': 0, 'bq': 0, 'br': 6, 'bs': 17, 'bx': 0, 'by': 0, 'bz': 0, '#g': 7, 'uy': 1, 'ux': 0, 'uz': 0, 'uu': 0, 'ut': 66, 'uw': 0, 'uv': 0, 'uq': 0, 'up': 0, 'us': 31, 'ur': 129, 'um': 2, 'ul': 39, 'uo': 1, 'un': 111, 'ui': 28, 'uh': 0, 'uk': 0, 'uj': 0, 'ue': 15, 'ud': 10, 'ug': 1, 'uf': 0, 'ua': 26, 'uc': 9, 'ub': 6, '#e': 20, 'nh': 0, 'ni': 191, 'nj': 0, 'nk': 0, 'nl': 0, 'nm': 17, 'nn': 144, 'no': 21, 'na': 21, 'nb': 0, 'nc': 42, 'nd': 71, 'ne': 68, 'nf': 1, 'ng': 160, 'nx': 0, 'ny': 2, 'nz': 0, 'np': 0, 'nq': 0, 'nr': 0, 'ns': 127, 'nt': 87, 'nu': 43, 'nv': 1, 'nw': 1, 'gw': 0, 'gv': 0, 'gu': 22, 'gt': 1, 'gs': 7, 'gr': 52, 'gq': 0, 'gp': 0, 'gz': 0, 'gy': 1, 'gx': 0, 'gg': 37, 'gf': 1, 'ge': 83, 'gd': 2, 'gc': 0, 'gb': 0, 'ga': 25, 'go': 4, 'gn': 29, 'gm': 0, 'gl': 3, 'gk': 0, 'gj': 0, 'gi': 39, 'gh': 25, 'zl': 0, 'zm': 0, 'zn': 0, 'zo': 0, 'zh': 0, 'zi': 0, 'zj': 0, 'zk': 0, 'zd': 0, 'ze': 2, 'zf': 0, 'zg': 0, 'za': 1, 'zb': 0, 'zc': 0, 'zx': 0, 'zy': 0, 'zz': 2, 'zt': 0, 'zu': 0, 'zv': 0, 'zw': 0, 'zp': 0, 'zq': 0, 'zr': 0, 'zs': 0, '#s': 26, '#q': 0, 'sz': 0, 'sy': 1, 'sx': 0, 'ss': 265, 'sr': 4, 'sq': 0, 'sp': 30, 'sw': 0, 'sv': 0, 'su': 21, 'st': 124, 'sk': 0, 'sj': 0, 'si': 231, 'sh': 18, 'so': 30, 'sn': 0, 'sm': 1, 'sl': 2, 'sc': 27, 'sb': 0, 'sa': 16, 'sg': 0, 'sf': 1, 'se': 74, 'sd': 0, 'lf': 0, 'lg': 0, 'ld': 6, 'le': 48, 'lb': 0, 'lc': 1, 'la': 24, 'ln': 0, 'lo': 29, 'll': 211, 'lm': 2, 'lj': 0, 'lk': 0, 'lh': 0, 'li': 217, 'lv': 2, 'lw': 0, 'lt': 7, 'lu': 3, 'lr': 2, 'ls': 12, 'lp': 0, 'lq': 0, 'lz': 0, 'lx': 0, 'ly': 11, 'em': 9, 'el': 32, 'eo': 19, 'en': 76, 'ei': 6, 'eh': 1, 'ek': 0, 'ej': 0, 'ee': 89, 'ed': 74, 'eg': 1, 'ef': 3, 'ea': 80, 'ec': 50, 'eb': 1, 'ey': 1, 'ex': 7, 'ez': 0, 'eu': 8, 'et': 34, 'ew': 1, 'ev': 2, 'eq': 1, 'ep': 9, 'es': 223, 'er': 237, 'xj': 0, 'xk': 0, 'xh': 1, 'xi': 0, 'xn': 0, 'xo': 0, 'xl': 0, 'xm': 0, 'xb': 0, 'xc': 17, 'xa': 1, 'xf': 0, 'xg': 0, 'xd': 0, 'xe': 3, 'xz': 0, 'xx': 0, 'xy': 1, 'xr': 0, 'xs': 0, 'xp': 6, 'xq': 0, 'xv': 0, 'xw': 0, 'xt': 5, 'xu': 0, '#f': 20, 'qq': 0, 'qp': 0, 'qs': 0, 'qr': 0, 'qu': 18, 'qt': 0, 'qw': 0, 'qv': 0, 'qy': 0, 'qx': 0, 'qz': 0, 'qa': 0, 'qc': 0, 'qb': 0, 'qe': 0, 'qd': 0, 'qg': 0, 'qf': 0, 'qi': 0, 'qh': 0, 'qk': 0, 'qj': 0, 'qm': 0, 'ql': 0, 'qo': 0, 'qn': 0, '#o': 5, '#n': 5, '#m': 16, '#c': 41, '#b': 14, '#a': 20, '#k': 6, '#j': 3, '#i': 20, '#h': 6, 'jx': 0, 'jy': 0, 'jz': 0, '#l': 22, 'jt': 0, 'ju': 1, 'jv': 0, 'jw': 0, 'jp': 0, 'jq': 0, 'jr': 0, 'js': 0, 'jl': 0, 'jm': 0, 'jn': 1, 'jo': 1, 'jh': 0, 'ji': 0, 'jj': 0, 'jk': 0, 'jd': 0, 'je': 1, 'jf': 0, 'jg': 0, '#w': 24, 'ja': 0, 'jb': 0, 'jc': 0, '#z': 2, '#y': 0, '#x': 0, 'ck': 9, 'cj': 0, 'ci': 320, 'ch': 24, 'co': 33, 'cn': 0, 'cm': 0, 'cl': 17, 'cc': 70, 'cb': 0, 'ca': 37, 'cg': 0, 'cf': 0, 'ce': 63, 'cd': 0, 'cz': 0, 'cy': 1, 'cx': 0, '#r': 28, 'cs': 6, 'cr': 46, 'cq': 0, 'cp': 0, 'cw': 0, 'cv': 0, 'cu': 17, 'ct': 54, '#d': 31, '#p': 17, '#v': 1, '#u': 2, '#t': 6, 'va': 9, 'vb': 0, 'vc': 0, 'vd': 0, 've': 58, 'vf': 0, 'vg': 0, 'vh': 0, 'vi': 31, 'vj': 0, 'vk': 0, 'vl': 0, 'vm': 0, 'vn': 0, 'vo': 2, 'vp': 0, 'vq': 0, 'vr': 1, 'vs': 0, 'vt': 0, 'vu': 0, 'vv': 0, 'vw': 0, 'vx': 0, 'vy': 1, 'vz': 0, 'oo': 26, 'on': 70, 'om': 9, 'ol': 13, 'ok': 0, 'oj': 1, 'oi': 4, 'oh': 0, 'og': 5, 'of': 0, 'oe': 8, 'od': 6, 'oc': 3, 'ob': 4, 'oa': 11, 'oz': 0, 'oy': 1, 'ox': 0, 'ow': 5, 'ov': 2, 'ou': 47, 'ot': 13, 'os': 20, 'or': 98, 'oq': 0, 'op': 20, 'hz': 0, 'hx': 0, 'hy': 1, 'hr': 15, 'hs': 1, 'hp': 0, 'hq': 0, 'hv': 0, 'hw': 1, 'ht': 26, 'hu': 0, 'hj': 0, 'hk': 0, 'hh': 25, 'hi': 24, 'hn': 9, 'ho': 22, 'hl': 7, 'hm': 1, 'hb': 12, 'hc': 1, 'ha': 15, 'hf': 0, 'hg': 0, 'hd': 3, 'he': 20, 'aa': 0, 'ac': 58, 'ab': 7, 'ae': 3, 'ad': 21, 'ag': 18, 'af': 5, 'ai': 61, 'ah': 8, 'ak': 4, 'aj': 0, 'am': 5, 'al': 43, 'ao': 0, 'an': 53, 'aq': 0, 'ap': 9, 'as': 28, 'ar': 98, 'au': 62, 'at': 53, 'aw': 0, 'av': 1, 'ay': 2, 'ax': 0, 'az': 0},
                                 'substitution': {'gw': 1, 'gv': 0, 'gu': 0, 'gt': 21, 'gs': 13, 'gr': 5, 'gq': 3, 'gp': 1, 'gz': 0, 'gy': 3, 'gx': 0, 'gg': 0, 'gf': 2, 'ge': 9, 'gd': 11, 'gc': 11, 'gb': 1, 'ga': 4, 'go': 2, 'gn': 0, 'gm': 0, 'gl': 3, 'gk': 1, 'gj': 1, 'gi': 0, 'gh': 0, 'tz': 6, 'tx': 0, 'ty': 7, 'tv': 2, 'tw': 19, 'tt': 0, 'tu': 0, 'tr': 11, 'ts': 37, 'tp': 6, 'tq': 0, 'tn': 5, 'to': 5, 'tl': 14, 'tm': 9, 'tj': 1, 'tk': 0, 'th': 5, 'ti': 0, 'tf': 5, 'tg': 19, 'td': 42, 'te': 7, 'tb': 4, 'tc': 9, 'ta': 3, 'vu': 0, 'zl': 7, 'zm': 5, 'zn': 0, 'zo': 0, 'zh': 0, 'zi': 0, 'zj': 0, 'zk': 0, 'zd': 7, 'ze': 0, 'zf': 0, 'zg': 0, 'za': 0, 'zb': 0, 'zc': 0, 'zx': 0, 'zy': 3, 'zz': 0, 'zt': 3, 'zu': 0, 'zv': 0, 'zw': 0, 'zp': 0, 'zq': 0, 'zr': 2, 'zs': 21, 'wl': 0, 'va': 0, 'vc': 7, 'wk': 1, 'vh': 0, 'wj': 0, 'vi': 0, 'vj': 0, 'vk': 0, 'vl': 1, 'vm': 0, 'wi': 0, 'vn': 0, 'vo': 1, 'me': 0, 'md': 8, 'mg': 0, 'mf': 2, 'ma': 1, 'mc': 7, 'mb': 3, 'mm': 0, 'ml': 4, 'mo': 0, 'mn': 180, 'mi': 0, 'mh': 6, 'mk': 4, 'mj': 0, 'mu': 13, 'mt': 15, 'mw': 2, 'mv': 3, 'mq': 0, 'mp': 6, 'ms': 9, 'mr': 0, 'vt': 3, 'my': 3, 'mx': 2, 'mz': 0, 'vv': 0, 'vw': 0, 'vx': 0, 'vz': 0, 'fp': 0, 'fq': 0, 'fr': 6, 'fs': 4, 'ft': 12, 'fu': 0, 'fv': 0, 'fw': 2, 'fx': 0, 'fy': 0, 'fz': 0, 'fa': 0, 'fb': 15, 'fc': 0, 'fd': 3, 'fe': 1, 'ff': 0, 'fg': 5, 'fh': 2, 'fi': 0, 'fj': 0, 'fk': 0, 'fl': 3, 'fm': 4, 'fn': 1, 'fo': 0, 'sz': 1, 'sy': 20, 'sx': 3, 'ss': 0, 'sr': 14, 'sq': 0, 'sp': 7, 'sw': 5, 'sv': 0, 'su': 0, 'st': 15, 'sk': 0, 'sj': 1, 'si': 0, 'sh': 1, 'so': 1, 'sn': 6, 'sm': 0, 'sl': 27, 'sc': 27, 'sb': 8, 'sa': 11, 'sg': 0, 'sf': 4, 'se': 35, 'sd': 33, 'lf': 4, 'lg': 5, 'ld': 4, 'le': 0, 'lb': 10, 'lc': 1, 'la': 2, 'ln': 14, 'lo': 2, 'll': 0, 'lm': 0, 'lj': 0, 'lk': 1, 'lh': 6, 'li': 13, 'lv': 0, 'lw': 0, 'lt': 2, 'lu': 0, 'lr': 11, 'ls': 10, 'lp': 5, 'lq': 0, 'lz': 0, 'lx': 0, 'ly': 0, 'wq': 0, 'yh': 7, 'yk': 0, 'yj': 0, 'ym': 2, 'yl': 0, 'yo': 6, 'yn': 0, 'ya': 0, 'yc': 2, 'yb': 0, 'ye': 15, 'yd': 0, 'yg': 1, 'yf': 0, 'yy': 0, 'yx': 1, 'yz': 0, 'yq': 0, 'yp': 1, 'ys': 36, 'yr': 7, 'yu': 5, 'yt': 8, 'yw': 0, 'yv': 0, 'em': 0, 'el': 3, 'eo': 93, 'en': 5, 'ei': 89, 'eh': 0, 'ek': 0, 'ej': 0, 'ee': 0, 'ed': 11, 'eg': 2, 'ef': 2, 'ea': 388, 'ec': 3, 'eb': 0, 'ey': 18, 'ex': 0, 'ez': 0, 'eu': 15, 'et': 6, 'ew': 1, 'ev': 0, 'eq': 0, 'ep': 0, 'es': 12, 'er': 14, 'rt': 22, 'ru': 4, 'rv': 0, 'rw': 0, 'rp': 14, 'rq': 0, 'rr': 0, 'rs': 12, 'rx': 1, 'ry': 0, 'rz': 0, 'rd': 30, 're': 12, 'rf': 2, 'rg': 2, 'ra': 0, 'rb': 14, 'rc': 0, 'rl': 8, 'rm': 4, 'rn': 20, 'ro': 1, 'rh': 8, 'ri': 2, 'rj': 0, 'rk': 5, 'xj': 0, 'xk': 0, 'xh': 0, 'xi': 0, 'xn': 0, 'xo': 0, 'xl': 0, 'xm': 0, 'xb': 0, 'xc': 0, 'xa': 0, 'xf': 0, 'xg': 0, 'xd': 2, 'xe': 0, 'xz': 0, 'xx': 0, 'xy': 0, 'xr': 0, 'xs': 9, 'xp': 0, 'xq': 0, 'xv': 0, 'xw': 0, 'xt': 0, 'xu': 0, 'wy': 0, 'wx': 0, 'kc': 8, 'kb': 2, 'ka': 1, 'kg': 2, 'kf': 1, 'ke': 1, 'kd': 4, 'kk': 0, 'kj': 0, 'ki': 0, 'kh': 5, 'ko': 2, 'kn': 0, 'km': 5, 'kl': 0, 'ks': 6, 'kr': 0, 'kq': 0, 'kp': 0, 'kw': 4, 'kv': 0, 'ku': 0, 'kt': 0, 'kz': 3, 'ky': 0, 'kx': 0, 'dn': 3, 'do': 0, 'dl': 3, 'dm': 7, 'dj': 0, 'dk': 2, 'dh': 5, 'di': 0, 'df': 0, 'dg': 5, 'dd': 0, 'de': 12, 'db': 10, 'dc': 13, 'da': 1, 'dz': 0, 'dx': 0, 'dy': 2, 'dv': 0, 'dw': 4, 'dt': 22, 'du': 0, 'dr': 43, 'ds': 30, 'dp': 1, 'dq': 0, 'qq': 0, 'qp': 0, 'qs': 0, 'qr': 0, 'qu': 0, 'qt': 0, 'qw': 0, 'qv': 0, 'qy': 0, 'qx': 0, 'qz': 0, 'qa': 0, 'qc': 1, 'qb': 0, 'qe': 0, 'qd': 0, 'qg': 27, 'qf': 0, 'qi': 0, 'qh': 0, 'qk': 0, 'qj': 0, 'qm': 0, 'ql': 0, 'qo': 0, 'qn': 0, 'wc': 1, 'wb': 2, 'wa': 2, 'wo': 0, 'wn': 0, 'wm': 0, 'wg': 0, 'wf': 0, 'we': 1, 'wd': 0, 'jx': 0, 'jy': 0, 'jz': 0, 'jt': 0, 'ju': 0, 'jv': 0, 'jw': 0, 'jp': 0, 'jq': 0, 'jr': 0, 'js': 5, 'jl': 2, 'jm': 1, 'jn': 0, 'jo': 0, 'jh': 0, 'ji': 0, 'jj': 0, 'jk': 0, 'jd': 9, 'je': 0, 'jf': 0, 'jg': 1, 'ja': 0, 'jb': 1, 'jc': 1, 'ww': 0, 'wv': 0, 'wu': 1, 'wt': 3, 'ws': 3, 'wr': 6, 'ck': 1, 'cj': 0, 'ci': 0, 'ch': 0, 'co': 1, 'cn': 9, 'cm': 7, 'cl': 0, 'cc': 0, 'cb': 5, 'ca': 6, 'wp': 7, 'cg': 5, 'cf': 9, 'ce': 0, 'cd': 16, 'cz': 0, 'cy': 1, 'cx': 1, 'cs': 39, 'cr': 5, 'cq': 2, 'cp': 10, 'cw': 7, 'cv': 3, 'cu': 1, 'ct': 40, 'pr': 1, 'ps': 3, 'pp': 0, 'pq': 0, 'pv': 4, 'pw': 1, 'pt': 6, 'pu': 0, 'pz': 0, 'px': 0, 'py': 0, 'wz': 0, 'pb': 11, 'pc': 1, 'pa': 0, 'pf': 6, 'pg': 5, 'pd': 2, 'pe': 0, 'pj': 9, 'pk': 0, 'ph': 0, 'pi': 2, 'pn': 6, 'po': 15, 'pl': 2, 'pm': 7, 'iy': 15, 'ix': 1, 'vb': 0, 'iz': 0, 'vd': 0, 've': 0, 'vf': 3, 'vg': 0, 'iq': 0, 'ip': 0, 'is': 2, 'ir': 0, 'iu': 47, 'it': 1, 'iw': 2, 'iv': 0, 'ii': 0, 'ih': 0, 'ik': 0, 'ij': 0, 'im': 0, 'il': 6, 'io': 49, 'in': 0, 'ia': 103, 'vy': 0, 'ic': 0, 'ib': 0, 'ie': 146, 'id': 0, 'ig': 1, 'if': 0, 'wh': 2, 'yi': 15, 'vr': 0, 'vs': 8, 'bd': 9, 'be': 2, 'bf': 2, 'bg': 3, 'ba': 0, 'bb': 0, 'bc': 9, 'bl': 5, 'bm': 11, 'bn': 5, 'bo': 0, 'bh': 1, 'bi': 0, 'bj': 0, 'bk': 0, 'bt': 1, 'bu': 0, 'bv': 0, 'bw': 8, 'bp': 10, 'bq': 0, 'br': 0, 'bs': 2, 'bx': 0, 'by': 0, 'bz': 0, 'oo': 0, 'on': 0, 'om': 0, 'ol': 0, 'ok': 2, 'oj': 0, 'oi': 25, 'oh': 0, 'og': 0, 'of': 0, 'oe': 116, 'od': 3, 'oc': 1, 'ob': 1, 'oa': 91, 'oz': 0, 'oy': 18, 'ox': 0, 'ow': 0, 'ov': 0, 'ou': 39, 'ot': 14, 'os': 4, 'or': 2, 'oq': 0, 'op': 14, 'hz': 0, 'hx': 0, 'hy': 0, 'hr': 3, 'hs': 1, 'hp': 3, 'hq': 0, 'hv': 0, 'hw': 2, 'ht': 11, 'hu': 0, 'hj': 0, 'hk': 2, 'hh': 0, 'hi': 0, 'hn': 14, 'ho': 2, 'hl': 0, 'hm': 12, 'hb': 8, 'hc': 0, 'ha': 1, 'hf': 0, 'hg': 0, 'hd': 3, 'he': 0, 'uy': 8, 'ux': 0, 'uz': 0, 'uu': 0, 'ut': 0, 'uw': 2, 'uv': 0, 'uq': 0, 'up': 0, 'us': 0, 'ur': 4, 'um': 0, 'ul': 0, 'uo': 43, 'un': 2, 'ui': 64, 'uh': 0, 'uk': 0, 'uj': 0, 'ue': 44, 'ud': 0, 'ug': 0, 'uf': 0, 'ua': 20, 'uc': 0, 'ub': 0, 'aa': 0, 'ac': 7, 'ab': 0, 'ae': 342, 'ad': 1, 'ag': 0, 'af': 0, 'ai': 118, 'ah': 2, 'ak': 1, 'aj': 0, 'am': 0, 'al': 0, 'ao': 76, 'an': 3, 'aq': 0, 'ap': 0, 'as': 35, 'ar': 1, 'au': 9, 'at': 9, 'aw': 1, 'av': 0, 'ay': 5, 'ax': 0, 'az': 0, 'nh': 19, 'ni': 1, 'nj': 0, 'nk': 4, 'nl': 35, 'nm': 78, 'nn': 0, 'no': 0, 'na': 2, 'nb': 7, 'nc': 6, 'nd': 5, 'ne': 3, 'nf': 0, 'ng': 1, 'nx': 2, 'ny': 0, 'nz': 2, 'np': 7, 'nq': 0, 'nr': 28, 'ns': 5, 'nt': 7, 'nu': 0, 'nv': 0, 'nw': 1, 'vp': 0, 'vq': 0},
                                 'transposition': {'gw': 0, 'gv': 0, 'gu': 3, 'gt': 0, 'gs': 0, 'gr': 3, 'gq': 0, 'gp': 0, 'gz': 0, 'gy': 0, 'gx': 0, 'gg': 0, 'gf': 0, 'ge': 2, 'gd': 0, 'gc': 0, 'gb': 0, 'ga': 4, 'go': 0, 'gn': 15, 'gm': 0, 'gl': 1, 'gk': 0, 'gj': 0, 'gi': 0, 'gh': 0, 'tz': 0, 'tx': 0, 'ty': 0, 'tv': 0, 'tw': 2, 'tt': 0, 'tu': 11, 'tr': 5, 'ts': 0, 'tp': 0, 'tq': 0, 'tn': 0, 'to': 3, 'tl': 4, 'tm': 0, 'tj': 0, 'tk': 0, 'th': 21, 'ti': 49, 'tf': 0, 'tg': 0, 'td': 0, 'te': 4, 'tb': 0, 'tc': 3, 'ta': 4, 'vu': 0, 'zl': 0, 'zm': 0, 'zn': 0, 'zo': 0, 'zh': 0, 'zi': 0, 'zj': 0, 'zk': 0, 'zd': 0, 'ze': 0, 'zf': 0, 'zg': 0, 'za': 0, 'zb': 0, 'zc': 0, 'zx': 0, 'zy': 0, 'zz': 0, 'zt': 0, 'zu': 0, 'zv': 0, 'zw': 0, 'zp': 0, 'zq': 0, 'zr': 0, 'zs': 0, 'wl': 0, 'va': 0, 'vc': 0, 'wk': 0, 'vh': 0, 'wj': 0, 'vi': 4, 'vj': 0, 'vk': 0, 'vl': 0, 'vm': 0, 'wi': 0, 'vn': 0, 'vo': 0, 'me': 20, 'md': 0, 'mg': 0, 'mf': 0, 'ma': 9, 'mc': 0, 'mb': 0, 'mm': 0, 'ml': 0, 'mo': 0, 'mn': 2, 'mi': 0, 'mh': 0, 'mk': 0, 'mj': 0, 'mu': 4, 'mt': 0, 'mw': 0, 'mv': 0, 'mq': 0, 'mp': 0, 'ms': 0, 'mr': 0, 'vt': 0, 'my': 0, 'mx': 0, 'mz': 0, 'vv': 0, 'vw': 0, 'vx': 0, 'vz': 0, 'fp': 0, 'fq': 0, 'fr': 0, 'fs': 0, 'ft': 0, 'fu': 0, 'fv': 0, 'fw': 0, 'fx': 0, 'fy': 0, 'fz': 0, 'fa': 0, 'fb': 0, 'fc': 0, 'fd': 0, 'fe': 0, 'ff': 0, 'fg': 0, 'fh': 0, 'fi': 12, 'fj': 0, 'fk': 0, 'fl': 1, 'fm': 0, 'fn': 0, 'fo': 0, 'sz': 0, 'sy': 16, 'sx': 0, 'ss': 0, 'sr': 0, 'sq': 0, 'sp': 22, 'sw': 0, 'sv': 0, 'su': 3, 'st': 1, 'sk': 0, 'sj': 0, 'si': 15, 'sh': 5, 'so': 1, 'sn': 0, 'sm': 2, 'sl': 5, 'sc': 0, 'sb': 0, 'sa': 4, 'sg': 0, 'sf': 0, 'se': 9, 'sd': 0, 'lf': 0, 'lg': 1, 'ld': 12, 'le': 20, 'lb': 0, 'lc': 0, 'la': 11, 'ln': 0, 'lo': 1, 'll': 0, 'lm': 0, 'lj': 0, 'lk': 0, 'lh': 0, 'li': 4, 'lv': 9, 'lw': 0, 'lt': 1, 'lu': 3, 'lr': 0, 'ls': 1, 'lp': 3, 'lq': 0, 'lz': 0, 'lx': 0, 'ly': 7, 'wq': 0, 'yh': 0, 'yk': 0, 'yj': 0, 'ym': 0, 'yl': 3, 'yo': 0, 'yn': 0, 'ya': 0, 'yc': 2, 'yb': 1, 'ye': 0, 'yd': 0, 'yg': 1, 'yf': 0, 'yy': 0, 'yx': 0, 'yz': 0, 'yq': 0, 'yp': 2, 'ys': 10, 'yr': 1, 'yu': 0, 'yt': 0, 'yw': 0, 'yv': 0, 'em': 6, 'el': 21, 'eo': 11, 'en': 16, 'ei': 60, 'eh': 0, 'ek': 0, 'ej': 0, 'ee': 0, 'ed': 5, 'eg': 0, 'ef': 0, 'ea': 1, 'ec': 4, 'eb': 0, 'ey': 2, 'ex': 0, 'ez': 0, 'eu': 85, 'et': 0, 'ew': 0, 'ev': 0, 'eq': 0, 'ep': 2, 'es': 5, 'er': 29, 'rt': 2, 'ru': 10, 'rv': 0, 'rw': 0, 'rp': 1, 'rq': 0, 'rr': 0, 'rs': 0, 'rx': 0, 'ry': 2, 'rz': 0, 'rd': 0, 're': 24, 'rf': 0, 'rg': 3, 'ra': 12, 'rb': 0, 'rc': 0, 'rl': 2, 'rm': 0, 'rn': 7, 'ro': 30, 'rh': 0, 'ri': 14, 'rj': 0, 'rk': 2, 'xj': 0, 'xk': 0, 'xh': 0, 'xi': 0, 'xn': 0, 'xo': 0, 'xl': 0, 'xm': 0, 'xb': 0, 'xc': 0, 'xa': 0, 'xf': 0, 'xg': 0, 'xd': 0, 'xe': 0, 'xz': 0, 'xx': 0, 'xy': 0, 'xr': 0, 'xs': 0, 'xp': 1, 'xq': 0, 'xv': 0, 'xw': 0, 'xt': 0, 'xu': 0, 'wy': 8, 'wx': 0, 'kc': 0, 'kb': 0, 'ka': 0, 'kg': 0, 'kf': 0, 'ke': 2, 'kd': 0, 'kk': 0, 'kj': 0, 'ki': 0, 'kh': 0, 'ko': 0, 'kn': 0, 'km': 0, 'kl': 0, 'ks': 0, 'kr': 0, 'kq': 0, 'kp': 0, 'kw': 0, 'kv': 0, 'ku': 0, 'kt': 0, 'kz': 0, 'ky': 0, 'kx': 0, 'dn': 0, 'do': 0, 'dl': 0, 'dm': 0, 'dj': 0, 'dk': 0, 'dh': 0, 'di': 7, 'df': 0, 'dg': 0, 'dd': 0, 'de': 0, 'db': 0, 'dc': 0, 'da': 0, 'dz': 0, 'dx': 0, 'dy': 0, 'dv': 0, 'dw': 0, 'dt': 0, 'du': 2, 'dr': 1, 'ds': 0, 'dp': 0, 'dq': 0, 'qq': 0, 'qp': 0, 'qs': 0, 'qr': 0, 'qu': 0, 'qt': 0, 'qw': 0, 'qv': 0, 'qy': 0, 'qx': 0, 'qz': 0, 'qa': 0, 'qc': 0, 'qb': 0, 'qe': 0, 'qd': 0, 'qg': 0, 'qf': 0, 'qi': 0, 'qh': 0, 'qk': 0, 'qj': 0, 'qm': 0, 'ql': 0, 'qo': 0, 'qn': 0, 'wc': 0, 'wb': 0, 'wa': 0, 'wo': 1, 'wn': 1, 'wm': 1, 'wg': 0, 'wf': 0, 'we': 0, 'wd': 0, 'jx': 0, 'jy': 0, 'jz': 0, 'jt': 0, 'ju': 0, 'jv': 0, 'jw': 0, 'jp': 0, 'jq': 0, 'jr': 0, 'js': 0, 'jl': 0, 'jm': 0, 'jn': 0, 'jo': 0, 'jh': 0, 'ji': 0, 'jj': 0, 'jk': 0, 'jd': 0, 'je': 0, 'jf': 0, 'jg': 0, 'ja': 0, 'jb': 0, 'jc': 0, 'ww': 0, 'wv': 0, 'wu': 0, 'wt': 0, 'ws': 0, 'wr': 0, 'ck': 0, 'cj': 0, 'ci': 85, 'ch': 1, 'co': 13, 'cn': 0, 'cm': 0, 'cl': 15, 'cc': 0, 'cb': 0, 'ca': 0, 'wp': 0, 'cg': 0, 'cf': 0, 'ce': 1, 'cd': 0, 'cz': 0, 'cy': 0, 'cx': 0, 'cs': 3, 'cr': 0, 'cq': 0, 'cp': 0, 'cw': 0, 'cv': 0, 'cu': 7, 'ct': 0, 'pr': 5, 'ps': 3, 'pp': 0, 'pq': 0, 'pv': 0, 'pw': 0, 'pt': 6, 'pu': 0, 'pz': 0, 'px': 0, 'py': 0, 'wz': 0, 'pb': 0, 'pc': 0, 'pa': 17, 'pf': 0, 'pg': 0, 'pd': 0, 'pe': 4, 'pj': 0, 'pk': 0, 'ph': 1, 'pi': 0, 'pn': 0, 'po': 1, 'pl': 0, 'pm': 0, 'iy': 0, 'ix': 0, 'vb': 0, 'iz': 3, 'vd': 0, 've': 1, 'vf': 0, 'vg': 0, 'iq': 1, 'ip': 0, 'is': 42, 'ir': 13, 'iu': 0, 'it': 35, 'iw': 0, 'iv': 6, 'ii': 0, 'ih': 0, 'ik': 0, 'ij': 0, 'im': 0, 'il': 9, 'io': 11, 'in': 5, 'ia': 15, 'vy': 0, 'ic': 31, 'ib': 8, 'ie': 66, 'id': 3, 'ig': 3, 'if': 1, 'wh': 4, 'yi': 0, 'vr': 0, 'vs': 0, 'bd': 0, 'be': 2, 'bf': 0, 'bg': 0, 'ba': 0, 'bb': 0, 'bc': 0, 'bl': 1, 'bm': 1, 'bn': 0, 'bo': 2, 'bh': 0, 'bi': 0, 'bj': 0, 'bk': 0, 'bt': 0, 'bu': 0, 'bv': 0, 'bw': 0, 'bp': 0, 'bq': 0, 'br': 0, 'bs': 2, 'bx': 0, 'by': 0, 'bz': 0, 'oo': 0, 'on': 5, 'om': 0, 'ol': 1, 'ok': 0, 'oj': 0, 'oi': 5, 'oh': 0, 'og': 0, 'of': 0, 'oe': 4, 'od': 0, 'oc': 2, 'ob': 0, 'oa': 5, 'oz': 0, 'oy': 0, 'ox': 1, 'ow': 7, 'ov': 0, 'ou': 0, 'ot': 1, 'os': 1, 'or': 11, 'oq': 0, 'op': 1, 'hz': 0, 'hx': 0, 'hy': 0, 'hr': 0, 'hs': 0, 'hp': 0, 'hq': 0, 'hv': 0, 'hw': 0, 'ht': 10, 'hu': 0, 'hj': 0, 'hk': 0, 'hh': 0, 'hi': 0, 'hn': 0, 'ho': 0, 'hl': 0, 'hm': 0, 'hb': 0, 'hc': 0, 'ha': 12, 'hf': 0, 'hg': 0, 'hd': 0, 'he': 15, 'uy': 0, 'ux': 0, 'uz': 0, 'uu': 0, 'ut': 2, 'uw': 0, 'uv': 0, 'uq': 0, 'up': 2, 'us': 11, 'ur': 11, 'um': 1, 'ul': 2, 'uo': 20, 'un': 0, 'ui': 2, 'uh': 0, 'uk': 0, 'uj': 0, 'ue': 1, 'ud': 1, 'ug': 2, 'uf': 0, 'ua': 22, 'uc': 5, 'ub': 0, 'aa': 0, 'ac': 2, 'ab': 0, 'ae': 1, 'ad': 1, 'ag': 0, 'af': 0, 'ai': 19, 'ah': 0, 'ak': 1, 'aj': 0, 'am': 4, 'al': 14, 'ao': 10, 'an': 25, 'aq': 0, 'ap': 3, 'as': 3, 'ar': 27, 'au': 31, 'at': 5, 'aw': 0, 'av': 0, 'ay': 0, 'ax': 0, 'az': 0, 'nh': 0, 'ni': 1, 'nj': 0, 'nk': 0, 'nl': 0, 'nm': 3, 'nn': 0, 'no': 0, 'na': 15, 'nb': 0, 'nc': 6, 'nd': 2, 'ne': 12, 'nf': 0, 'ng': 8, 'nx': 0, 'ny': 0, 'nz': 0, 'np': 0, 'nq': 0, 'nr': 0, 'ns': 6, 'nt': 4, 'nu': 0, 'nv': 0, 'nw': 0, 'vp': 0, 'vq': 0}}

    def add_language_model(self, lm):
        """
        Add or replace the language model used by the spell checker.

        Parameters:
        -----------
        lm : LanguageModel
            A language model object used for token probability calculations.
        """
        self.lm = lm

    def add_error_tables(self, error_tables):
        """
        Add or replace the error tables used for spelling correction.

        Parameters:
        -----------
        error_tables : dict
            A dictionary of error tables representing various types of spelling errors (insertion, deletion, substitution, and transposition).
            The dictionary is in the format of the confusion matrices shown in the link:
            https://www.dropbox.com/s/ic40soda29emt4a/spelling_confusion_matrices.py?dl=0
        """
        self.error_tables = error_tables
        if self.error_tables == None:
            self.error_tables = {'insertion': {'gw': 1, 'gv': 0, 'gu': 3, 'gt': 2, 'gs': 69, 'gr': 5, 'gq': 1, 'gp': 0, '#y': 1, 'gz': 0, 'gy': 0, 'gx': 0, 'gg': 5, 'gf': 1, 'ge': 5, 'gd': 0, 'gc': 0, 'gb': 0, 'ga': 8, 'go': 1, 'gn': 1, 'gm': 0, 'gl': 2, 'gk': 0, 'gj': 0, 'gi': 8, 'gh': 12, 'tz': 0, 'tx': 0, 'ty': 6, 'tv': 0, 'tw': 5, 'tt': 183, 'tu': 11, 'tr': 54, 'ts': 264, 'tp': 1, 'tq': 0, 'tn': 1, 'to': 23, 'tl': 6, 'tm': 3, 'tj': 1, 'tk': 0, 'th': 24, 'ti': 59, 'tf': 1, 'tg': 10, 'td': 3, 'te': 65, 'tb': 0, 'tc': 0, 'ta': 39, 'vu': 1, 'zl': 0, 'zm': 0, 'zn': 0, 'zo': 0, 'zh': 0, 'zi': 6, 'zj': 0, 'zk': 0, 'zd': 0, 'ze': 5, 'zf': 1, 'zg': 0, 'za': 2, 'zb': 0, 'zc': 0, 'zx': 0, 'zy': 2, 'zz': 4, 'zt': 0, 'zu': 0, 'zv': 0, 'zw': 0, 'zp': 0, 'zq': 0, 'zr': 0, 'zs': 0, '#s': 23, 'wl': 1, '#q': 0, 'va': 0, '#c': 9, 'vc': 0, 'wk': 1, '#p': 10, 'vh': 0, 'wj': 0, 'vi': 10, 'vj': 0, 'vk': 0, 'vl': 1, 'vm': 0, 'wi': 1, '#v': 1, 'vn': 1, 'vo': 0, 'me': 17, 'md': 0, 'mg': 0, 'mf': 0, 'ma': 11, 'mc': 1, 'mb': 1, 'mm': 102, 'ml': 0, 'mo': 7, 'mn': 44, 'mi': 6, 'mh': 1, 'mk': 1, 'mj': 0, 'mu': 2, 'mt': 1, 'mw': 1, 'mv': 0, 'mq': 0, 'mp': 2, 'ms': 47, 'mr': 0, 'vt': 0, 'my': 0, 'mx': 0, 'mz': 0, 'vv': 5, 'vw': 1, '#t': 2, 'vx': 0, 'vz': 0, '#b': 8, 'fp': 0, 'fq': 0, 'fr': 5, 'fs': 23, 'ft': 0, 'fu': 1, 'fv': 0, 'fw': 0, 'fx': 0, 'fy': 1, 'fz': 0, 'fa': 1, 'fb': 0, 'fc': 0, 'fd': 0, 'fe': 2, 'ff': 27, 'fg': 1, 'fh': 0, 'fi': 12, 'fj': 0, 'fk': 0, 'fl': 10, 'fm': 0, 'fn': 0, 'fo': 0, 'sz': 0, 'sy': 7, 'sx': 0, 'ss': 205, 'sr': 1, 'sq': 0, 'sp': 1, 'sw': 1, 'sv': 0, 'su': 7, 'st': 49, 'sk': 2, 'sj': 0, 'si': 101, 'sh': 50, 'so': 3, 'sn': 7, 'sm': 10, 'sl': 2, 'sc': 7, 'sb': 1, 'sa': 13, 'sg': 1, 'sf': 0, 'se': 41, 'sd': 20, 'lf': 0, 'lg': 0, 'ld': 1, 'le': 38, 'lb': 1, 'lc': 0, 'la': 3, 'ln': 0, 'lo': 7, 'll': 128, 'lm': 1, 'lj': 0, 'lk': 2, 'lh': 0, 'li': 79, 'lv': 1, 'lw': 0, 'lt': 7, 'lu': 3, 'lr': 0, 'ls': 97, 'lp': 0, 'lq': 0, 'lz': 0, 'lx': 0, 'ly': 2, 'wq': 1, 'yh': 0, 'yk': 0, 'yj': 0, 'ym': 1, 'yl': 1, 'yo': 0, 'yn': 6, 'ya': 5, 'yc': 2, 'yb': 1, 'ye': 3, 'yd': 0, 'yg': 0, 'yf': 0, 'yy': 2, 'yx': 0, 'yz': 0, 'yq': 0, 'yp': 0, 'ys': 33, 'yr': 1, 'yu': 13, 'yt': 1, 'yw': 1, 'yv': 0, 'em': 6, 'el': 4, 'eo': 5, 'en': 27, 'ei': 4, 'eh': 1, 'ek': 3, 'ej': 0, 'ee': 147, 'ed': 76, 'eg': 0, 'ef': 2, 'ea': 39, 'ec': 8, 'eb': 2, 'ey': 8, 'ex': 2, '#g': 14, 'ez': 0, 'eu': 4, 'et': 6, 'ew': 10, 'ev': 1, 'eq': 0, 'ep': 1, 'es': 417, 'er': 83, 'rt': 29, 'ru': 7, 'rv': 0, 'rw': 1, 'rp': 0, 'rq': 0, 'rr': 132, 'rs': 273, 'rx': 0, 'ry': 10, 'rz': 0, 'rd': 0, 're': 89, 'rf': 1, 'rg': 1, 'ra': 15, 'rb': 2, 'rc': 1, 'rl': 5, 'rm': 9, 'rn': 7, 'ro': 10, 'rh': 2, 'ri': 64, 'rj': 0, 'rk': 0, 'xj': 0, 'xk': 0, 'xh': 6, 'xi': 1, 'xn': 0, 'xo': 3, 'xl': 0, 'xm': 1, 'xb': 0, 'xc': 18, 'xa': 0, 'xf': 0, 'xg': 0, 'xd': 0, 'xe': 1, 'xz': 0, 'xx': 1, 'xy': 0, 'xr': 0, 'xs': 2, 'xp': 0, 'xq': 0, 'xv': 0, 'xw': 0, 'xt': 0, 'xu': 0, 'wy': 0, 'wx': 0, '#d': 8, 'kc': 0, 'kb': 4, 'ka': 2, 'kg': 0, 'kf': 0, 'ke': 9, 'kd': 1, 'kk': 1, 'kj': 0, 'ki': 1, 'kh': 1, 'ko': 2, 'kn': 0, 'km': 0, 'kl': 1, 'ks': 95, 'kr': 0, 'kq': 0, 'kp': 1, 'kw': 0, 'kv': 0, 'ku': 1, 'kt': 0, 'kz': 0, 'ky': 4, 'kx': 0, 'dn': 9, 'do': 13, 'dl': 6, 'dm': 1, 'dj': 0, 'dk': 0, 'dh': 0, 'di': 9, 'df': 2, 'dg': 0, 'dd': 17, 'de': 14, 'db': 0, 'dc': 3, 'da': 18, 'dz': 0, 'dx': 0, 'dy': 5, 'dv': 0, 'dw': 0, 'dt': 0, 'du': 0, 'dr': 6, 'ds': 119, 'dp': 0, 'dq': 0, 'qq': 0, 'qp': 0, 'qs': 0, 'qr': 0, 'qu': 1, 'qt': 0, 'qw': 0, 'qv': 0, 'qy': 0, 'qx': 0, 'qz': 0, 'qa': 0, 'qc': 0, 'qb': 0, 'qe': 0, 'qd': 0, 'qg': 0, 'qf': 0, 'qi': 1, 'qh': 0, 'qk': 0, 'qj': 0, 'qm': 0, 'ql': 0, 'qo': 0, 'qn': 0, '#k': 17, '#j': 1, '#e': 26, '#i': 5, '#h': 3, 'wc': 0, 'wb': 0, 'wa': 0, 'wo': 0, 'wn': 2, 'wm': 0, 'wg': 0, 'wf': 0, 'we': 10, 'wd': 1, 'jx': 0, 'jy': 0, 'jz': 0, '#l': 5, 'jt': 0, 'ju': 1, 'jv': 0, 'jw': 0, 'jp': 0, 'jq': 0, 'jr': 0, 'js': 0, 'jl': 0, 'jm': 0, 'jn': 0, 'jo': 0, 'jh': 0, 'ji': 0, 'jj': 0, 'jk': 0, 'jd': 0, 'je': 0, 'jf': 0, 'jg': 0, '#w': 2, 'ja': 0, 'jb': 0, 'jc': 0, 'ww': 4, 'wv': 0, 'wu': 2, 'wt': 0, 'ws': 8, 'wr': 1, 'ck': 3, 'cj': 0, 'ci': 50, 'ch': 18, 'co': 7, 'cn': 1, 'cm': 1, 'cl': 1, 'cc': 54, 'cb': 0, 'ca': 19, 'wp': 0, 'cg': 0, 'cf': 0, 'ce': 13, 'cd': 1, 'cz': 0, 'cy': 0, 'cx': 1, '#r': 6, 'cs': 25, 'cr': 7, 'cq': 0, 'cp': 1, 'cw': 0, 'cv': 4, 'cu': 8, 'ct': 7, 'pr': 29, 'ps': 52, 'pp': 70, 'pq': 0, 'pv': 1, 'pw': 1, 'pt': 9, 'pu': 1, 'pz': 0, 'px': 0, 'py': 0, 'wz': 0, 'pb': 0, 'pc': 1, 'pa': 23, 'pf': 0, 'pg': 0, 'pd': 1, 'pe': 10, 'pj': 0, 'pk': 0, 'ph': 20, 'pi': 3, 'pn': 0, 'po': 26, 'pl': 2, 'pm': 0, 'iy': 0, 'ix': 1, 'vb': 2, 'iz': 1, 'vd': 0, 've': 36, 'vf': 0, 'vg': 0, 'iq': 0, 'ip': 1, 'is': 30, 'ir': 9, 'iu': 11, 'it': 29, 'iw': 0, 'iv': 0, 'ii': 69, 'ih': 1, 'ik': 1, 'ij': 2, 'im': 11, 'il': 17, 'io': 27, 'in': 33, 'ia': 10, 'vy': 0, 'ic': 13, 'ib': 3, 'ie': 25, 'id': 13, 'ig': 1, 'if': 0, '#x': 1, 'wh': 1, 'yi': 2, '#u': 11, 'vr': 0, '#f': 11, '#o': 2, '#n': 2, '#m': 6, 'vs': 0, 'bd': 0, 'be': 7, 'bf': 0, 'bg': 1, 'ba': 3, 'bb': 11, 'bc': 0, 'bl': 15, 'bm': 0, 'bn': 1, 'bo': 1, 'bh': 0, 'bi': 50, 'bj': 0, 'bk': 0, 'bt': 0, 'bu': 0, 'bv': 3, 'bw': 0, 'bp': 0, 'bq': 0, 'br': 5, 'bs': 16, 'bx': 0, 'by': 0, 'bz': 0, 'oo': 64, 'on': 13, 'om': 3, 'ol': 6, 'ok': 0, 'oj': 1, 'oi': 28, 'oh': 0, 'og': 1, 'of': 2, 'oe': 7, 'od': 3, 'oc': 1, 'ob': 1, 'oa': 14, 'oz': 1, 'oy': 1, 'ox': 0, 'ow': 0, 'ov': 1, 'ou': 19, 'ot': 4, 'os': 59, 'or': 16, 'oq': 0, 'op': 30, '#a': 46, 'hz': 0, 'hx': 0, 'hy': 3, 'hr': 16, 'hs': 24, 'hp': 0, 'hq': 0, 'hv': 0, 'hw': 5, 'ht': 22, 'hu': 1, 'hj': 2, 'hk': 0, 'hh': 18, 'hi': 17, 'hn': 1, 'ho': 4, 'hl': 1, 'hm': 0, 'hb': 1, 'hc': 0, 'ha': 4, 'hf': 0, 'hg': 10, 'hd': 1, 'he': 24, 'uy': 3, 'ux': 2, 'uz': 0, 'uu': 26, 'ut': 27, 'uw': 0, 'uv': 0, 'uq': 0, 'up': 3, 'us': 19, 'ur': 49, 'um': 3, 'ul': 3, 'uo': 1, 'un': 9, 'ui': 24, 'uh': 1, 'uk': 1, 'uj': 1, 'ue': 9, 'ud': 0, 'ug': 0, 'uf': 0, 'ua': 15, 'uc': 3, 'ub': 0, 'aa': 15, 'ac': 14, 'ab': 1, 'ae': 10, 'ad': 7, 'ag': 1, 'af': 0, 'ai': 33, 'ah': 1, 'ak': 4, 'aj': 1, 'am': 2, 'al': 31, 'ao': 12, 'an': 39, 'aq': 3, 'ap': 4, 'as': 134, 'ar': 28, 'au': 28, 'at': 7, 'aw': 1, 'av': 0, 'ay': 4, 'ax': 1, 'az': 1, 'nh': 0, 'ni': 34, 'nj': 0, 'nk': 1, 'nl': 1, 'nm': 26, 'nn': 99, 'no': 12, 'na': 15, 'nb': 5, 'nc': 7, 'nd': 13, 'ne': 52, 'nf': 4, 'ng': 17, 'nx': 0, 'ny': 1, 'nz': 0, 'np': 0, 'nq': 0, 'nr': 2, 'ns': 156, 'nt': 53, 'nu': 1, 'nv': 1, 'nw': 0, 'vp': 1, '#z': 2, 'vq': 0},
                                 'deletion': {'tz': 0, 'tx': 0, 'ty': 2, 'tv': 0, 'tw': 4, 'tt': 137, 'tu': 14, 'tr': 203, 'ts': 5, 'tp': 1, 'tq': 0, 'tn': 3, 'to': 11, 'tl': 31, 'tm': 3, 'tj': 0, 'tk': 0, 'th': 49, 'ti': 427, 'tf': 1, 'tg': 7, 'td': 0, 'te': 76, 'tb': 1, 'tc': 2, 'ta': 24, 'me': 33, 'md': 0, 'mg': 0, 'mf': 0, 'ma': 15, 'mc': 0, 'mb': 10, 'mm': 180, 'ml': 0, 'mo': 7, 'mn': 7, 'mi': 42, 'mh': 1, 'mk': 0, 'mj': 0, 'mu': 4, 'mt': 0, 'mw': 0, 'mv': 0, 'mq': 0, 'mp': 31, 'ms': 9, 'mr': 0, 'my': 0, 'mx': 0, 'mz': 0, 'fp': 0, 'fq': 0, 'fr': 11, 'fs': 0, 'ft': 8, 'fu': 1, 'fv': 0, 'fw': 0, 'fx': 0, 'fy': 1, 'fz': 0, 'fa': 4, 'fb': 0, 'fc': 0, 'fd': 0, 'fe': 13, 'ff': 46, 'fg': 0, 'fh': 0, 'fi': 79, 'fj': 0, 'fk': 0, 'fl': 12, 'fm': 0, 'fn': 0, 'fo': 4, 'yi': 1, 'yh': 0, 'yk': 0, 'yj': 0, 'ym': 2, 'yl': 1, 'yo': 1, 'yn': 1, 'ya': 2, 'yc': 34, 'yb': 1, 'ye': 2, 'yd': 0, 'yg': 1, 'yf': 0, 'yy': 0, 'yx': 0, 'yz': 0, 'yq': 0, 'yp': 1, 'ys': 17, 'yr': 0, 'yu': 0, 'yt': 1, 'yw': 1, 'yv': 0, 'rt': 68, 'ru': 0, 'rv': 10, 'rw': 1, 'rp': 2, 'rq': 0, 'rr': 277, 'rs': 103, 'rx': 0, 'ry': 27, 'rz': 0, 'rd': 19, 're': 188, 'rf': 0, 'rg': 11, 'ra': 63, 'rb': 4, 'rc': 12, 'rl': 33, 'rm': 7, 'rn': 157, 'ro': 21, 'rh': 5, 'ri': 132, 'rj': 0, 'rk': 3, 'kc': 0, 'kb': 0, 'ka': 4, 'kg': 8, 'kf': 1, 'ke': 15, 'kd': 1, 'kk': 1, 'kj': 0, 'ki': 5, 'kh': 1, 'ko': 0, 'kn': 17, 'km': 0, 'kl': 3, 'ks': 5, 'kr': 1, 'kq': 0, 'kp': 0, 'kw': 1, 'kv': 0, 'ku': 0, 'kt': 0, 'kz': 0, 'ky': 0, 'kx': 0, 'dn': 3, 'do': 3, 'dl': 8, 'dm': 4, 'dj': 1, 'dk': 1, 'dh': 0, 'di': 62, 'df': 0, 'dg': 10, 'dd': 25, 'de': 45, 'db': 0, 'dc': 7, 'da': 12, 'dz': 0, 'dx': 0, 'dy': 6, 'dv': 2, 'dw': 0, 'dt': 0, 'du': 3, 'dr': 11, 'ds': 1, 'dp': 0, 'dq': 0, 'wg': 0, 'wf': 1, 'we': 11, 'wd': 1, 'wc': 0, 'wb': 0, 'wa': 40, 'wo': 2, 'wn': 2, 'wm': 0, 'wl': 1, 'wk': 0, 'wj': 0, 'wi': 15, 'wh': 11, 'ww': 0, 'wv': 0, 'wu': 0, 'wt': 0, 'ws': 24, 'wr': 2, 'wq': 0, 'wp': 0, 'wz': 0, 'wy': 0, 'wx': 0, 'pr': 58, 'ps': 1, 'pp': 93, 'pq': 0, 'pv': 0, 'pw': 0, 'pt': 18, 'pu': 2, 'pz': 0, 'px': 0, 'py': 0, 'pb': 0, 'pc': 0, 'pa': 25, 'pf': 0, 'pg': 0, 'pd': 0, 'pe': 22, 'pj': 0, 'pk': 0, 'ph': 12, 'pi': 15, 'pn': 0, 'po': 30, 'pl': 28, 'pm': 1, 'iy': 1, 'ix': 0, 'iz': 7, 'iq': 0, 'ip': 7, 'is': 71, 'ir': 16, 'iu': 1, 'it': 64, 'iw': 0, 'iv': 1, 'ii': 1, 'ih': 0, 'ik': 0, 'ij': 0, 'im': 14, 'il': 38, 'io': 41, 'in': 82, 'ia': 26, 'ic': 60, 'ib': 1, 'ie': 23, 'id': 26, 'ig': 9, 'if': 1, 'bd': 0, 'be': 22, 'bf': 0, 'bg': 0, 'ba': 2, 'bb': 2, 'bc': 1, 'bl': 26, 'bm': 0, 'bn': 0, 'bo': 2, 'bh': 0, 'bi': 183, 'bj': 0, 'bk': 0, 'bt': 0, 'bu': 6, 'bv': 1, 'bw': 0, 'bp': 0, 'bq': 0, 'br': 6, 'bs': 17, 'bx': 0, 'by': 0, 'bz': 0, '#g': 7, 'uy': 1, 'ux': 0, 'uz': 0, 'uu': 0, 'ut': 66, 'uw': 0, 'uv': 0, 'uq': 0, 'up': 0, 'us': 31, 'ur': 129, 'um': 2, 'ul': 39, 'uo': 1, 'un': 111, 'ui': 28, 'uh': 0, 'uk': 0, 'uj': 0, 'ue': 15, 'ud': 10, 'ug': 1, 'uf': 0, 'ua': 26, 'uc': 9, 'ub': 6, '#e': 20, 'nh': 0, 'ni': 191, 'nj': 0, 'nk': 0, 'nl': 0, 'nm': 17, 'nn': 144, 'no': 21, 'na': 21, 'nb': 0, 'nc': 42, 'nd': 71, 'ne': 68, 'nf': 1, 'ng': 160, 'nx': 0, 'ny': 2, 'nz': 0, 'np': 0, 'nq': 0, 'nr': 0, 'ns': 127, 'nt': 87, 'nu': 43, 'nv': 1, 'nw': 1, 'gw': 0, 'gv': 0, 'gu': 22, 'gt': 1, 'gs': 7, 'gr': 52, 'gq': 0, 'gp': 0, 'gz': 0, 'gy': 1, 'gx': 0, 'gg': 37, 'gf': 1, 'ge': 83, 'gd': 2, 'gc': 0, 'gb': 0, 'ga': 25, 'go': 4, 'gn': 29, 'gm': 0, 'gl': 3, 'gk': 0, 'gj': 0, 'gi': 39, 'gh': 25, 'zl': 0, 'zm': 0, 'zn': 0, 'zo': 0, 'zh': 0, 'zi': 0, 'zj': 0, 'zk': 0, 'zd': 0, 'ze': 2, 'zf': 0, 'zg': 0, 'za': 1, 'zb': 0, 'zc': 0, 'zx': 0, 'zy': 0, 'zz': 2, 'zt': 0, 'zu': 0, 'zv': 0, 'zw': 0, 'zp': 0, 'zq': 0, 'zr': 0, 'zs': 0, '#s': 26, '#q': 0, 'sz': 0, 'sy': 1, 'sx': 0, 'ss': 265, 'sr': 4, 'sq': 0, 'sp': 30, 'sw': 0, 'sv': 0, 'su': 21, 'st': 124, 'sk': 0, 'sj': 0, 'si': 231, 'sh': 18, 'so': 30, 'sn': 0, 'sm': 1, 'sl': 2, 'sc': 27, 'sb': 0, 'sa': 16, 'sg': 0, 'sf': 1, 'se': 74, 'sd': 0, 'lf': 0, 'lg': 0, 'ld': 6, 'le': 48, 'lb': 0, 'lc': 1, 'la': 24, 'ln': 0, 'lo': 29, 'll': 211, 'lm': 2, 'lj': 0, 'lk': 0, 'lh': 0, 'li': 217, 'lv': 2, 'lw': 0, 'lt': 7, 'lu': 3, 'lr': 2, 'ls': 12, 'lp': 0, 'lq': 0, 'lz': 0, 'lx': 0, 'ly': 11, 'em': 9, 'el': 32, 'eo': 19, 'en': 76, 'ei': 6, 'eh': 1, 'ek': 0, 'ej': 0, 'ee': 89, 'ed': 74, 'eg': 1, 'ef': 3, 'ea': 80, 'ec': 50, 'eb': 1, 'ey': 1, 'ex': 7, 'ez': 0, 'eu': 8, 'et': 34, 'ew': 1, 'ev': 2, 'eq': 1, 'ep': 9, 'es': 223, 'er': 237, 'xj': 0, 'xk': 0, 'xh': 1, 'xi': 0, 'xn': 0, 'xo': 0, 'xl': 0, 'xm': 0, 'xb': 0, 'xc': 17, 'xa': 1, 'xf': 0, 'xg': 0, 'xd': 0, 'xe': 3, 'xz': 0, 'xx': 0, 'xy': 1, 'xr': 0, 'xs': 0, 'xp': 6, 'xq': 0, 'xv': 0, 'xw': 0, 'xt': 5, 'xu': 0, '#f': 20, 'qq': 0, 'qp': 0, 'qs': 0, 'qr': 0, 'qu': 18, 'qt': 0, 'qw': 0, 'qv': 0, 'qy': 0, 'qx': 0, 'qz': 0, 'qa': 0, 'qc': 0, 'qb': 0, 'qe': 0, 'qd': 0, 'qg': 0, 'qf': 0, 'qi': 0, 'qh': 0, 'qk': 0, 'qj': 0, 'qm': 0, 'ql': 0, 'qo': 0, 'qn': 0, '#o': 5, '#n': 5, '#m': 16, '#c': 41, '#b': 14, '#a': 20, '#k': 6, '#j': 3, '#i': 20, '#h': 6, 'jx': 0, 'jy': 0, 'jz': 0, '#l': 22, 'jt': 0, 'ju': 1, 'jv': 0, 'jw': 0, 'jp': 0, 'jq': 0, 'jr': 0, 'js': 0, 'jl': 0, 'jm': 0, 'jn': 1, 'jo': 1, 'jh': 0, 'ji': 0, 'jj': 0, 'jk': 0, 'jd': 0, 'je': 1, 'jf': 0, 'jg': 0, '#w': 24, 'ja': 0, 'jb': 0, 'jc': 0, '#z': 2, '#y': 0, '#x': 0, 'ck': 9, 'cj': 0, 'ci': 320, 'ch': 24, 'co': 33, 'cn': 0, 'cm': 0, 'cl': 17, 'cc': 70, 'cb': 0, 'ca': 37, 'cg': 0, 'cf': 0, 'ce': 63, 'cd': 0, 'cz': 0, 'cy': 1, 'cx': 0, '#r': 28, 'cs': 6, 'cr': 46, 'cq': 0, 'cp': 0, 'cw': 0, 'cv': 0, 'cu': 17, 'ct': 54, '#d': 31, '#p': 17, '#v': 1, '#u': 2, '#t': 6, 'va': 9, 'vb': 0, 'vc': 0, 'vd': 0, 've': 58, 'vf': 0, 'vg': 0, 'vh': 0, 'vi': 31, 'vj': 0, 'vk': 0, 'vl': 0, 'vm': 0, 'vn': 0, 'vo': 2, 'vp': 0, 'vq': 0, 'vr': 1, 'vs': 0, 'vt': 0, 'vu': 0, 'vv': 0, 'vw': 0, 'vx': 0, 'vy': 1, 'vz': 0, 'oo': 26, 'on': 70, 'om': 9, 'ol': 13, 'ok': 0, 'oj': 1, 'oi': 4, 'oh': 0, 'og': 5, 'of': 0, 'oe': 8, 'od': 6, 'oc': 3, 'ob': 4, 'oa': 11, 'oz': 0, 'oy': 1, 'ox': 0, 'ow': 5, 'ov': 2, 'ou': 47, 'ot': 13, 'os': 20, 'or': 98, 'oq': 0, 'op': 20, 'hz': 0, 'hx': 0, 'hy': 1, 'hr': 15, 'hs': 1, 'hp': 0, 'hq': 0, 'hv': 0, 'hw': 1, 'ht': 26, 'hu': 0, 'hj': 0, 'hk': 0, 'hh': 25, 'hi': 24, 'hn': 9, 'ho': 22, 'hl': 7, 'hm': 1, 'hb': 12, 'hc': 1, 'ha': 15, 'hf': 0, 'hg': 0, 'hd': 3, 'he': 20, 'aa': 0, 'ac': 58, 'ab': 7, 'ae': 3, 'ad': 21, 'ag': 18, 'af': 5, 'ai': 61, 'ah': 8, 'ak': 4, 'aj': 0, 'am': 5, 'al': 43, 'ao': 0, 'an': 53, 'aq': 0, 'ap': 9, 'as': 28, 'ar': 98, 'au': 62, 'at': 53, 'aw': 0, 'av': 1, 'ay': 2, 'ax': 0, 'az': 0},
                                 'substitution': {'gw': 1, 'gv': 0, 'gu': 0, 'gt': 21, 'gs': 13, 'gr': 5, 'gq': 3, 'gp': 1, 'gz': 0, 'gy': 3, 'gx': 0, 'gg': 0, 'gf': 2, 'ge': 9, 'gd': 11, 'gc': 11, 'gb': 1, 'ga': 4, 'go': 2, 'gn': 0, 'gm': 0, 'gl': 3, 'gk': 1, 'gj': 1, 'gi': 0, 'gh': 0, 'tz': 6, 'tx': 0, 'ty': 7, 'tv': 2, 'tw': 19, 'tt': 0, 'tu': 0, 'tr': 11, 'ts': 37, 'tp': 6, 'tq': 0, 'tn': 5, 'to': 5, 'tl': 14, 'tm': 9, 'tj': 1, 'tk': 0, 'th': 5, 'ti': 0, 'tf': 5, 'tg': 19, 'td': 42, 'te': 7, 'tb': 4, 'tc': 9, 'ta': 3, 'vu': 0, 'zl': 7, 'zm': 5, 'zn': 0, 'zo': 0, 'zh': 0, 'zi': 0, 'zj': 0, 'zk': 0, 'zd': 7, 'ze': 0, 'zf': 0, 'zg': 0, 'za': 0, 'zb': 0, 'zc': 0, 'zx': 0, 'zy': 3, 'zz': 0, 'zt': 3, 'zu': 0, 'zv': 0, 'zw': 0, 'zp': 0, 'zq': 0, 'zr': 2, 'zs': 21, 'wl': 0, 'va': 0, 'vc': 7, 'wk': 1, 'vh': 0, 'wj': 0, 'vi': 0, 'vj': 0, 'vk': 0, 'vl': 1, 'vm': 0, 'wi': 0, 'vn': 0, 'vo': 1, 'me': 0, 'md': 8, 'mg': 0, 'mf': 2, 'ma': 1, 'mc': 7, 'mb': 3, 'mm': 0, 'ml': 4, 'mo': 0, 'mn': 180, 'mi': 0, 'mh': 6, 'mk': 4, 'mj': 0, 'mu': 13, 'mt': 15, 'mw': 2, 'mv': 3, 'mq': 0, 'mp': 6, 'ms': 9, 'mr': 0, 'vt': 3, 'my': 3, 'mx': 2, 'mz': 0, 'vv': 0, 'vw': 0, 'vx': 0, 'vz': 0, 'fp': 0, 'fq': 0, 'fr': 6, 'fs': 4, 'ft': 12, 'fu': 0, 'fv': 0, 'fw': 2, 'fx': 0, 'fy': 0, 'fz': 0, 'fa': 0, 'fb': 15, 'fc': 0, 'fd': 3, 'fe': 1, 'ff': 0, 'fg': 5, 'fh': 2, 'fi': 0, 'fj': 0, 'fk': 0, 'fl': 3, 'fm': 4, 'fn': 1, 'fo': 0, 'sz': 1, 'sy': 20, 'sx': 3, 'ss': 0, 'sr': 14, 'sq': 0, 'sp': 7, 'sw': 5, 'sv': 0, 'su': 0, 'st': 15, 'sk': 0, 'sj': 1, 'si': 0, 'sh': 1, 'so': 1, 'sn': 6, 'sm': 0, 'sl': 27, 'sc': 27, 'sb': 8, 'sa': 11, 'sg': 0, 'sf': 4, 'se': 35, 'sd': 33, 'lf': 4, 'lg': 5, 'ld': 4, 'le': 0, 'lb': 10, 'lc': 1, 'la': 2, 'ln': 14, 'lo': 2, 'll': 0, 'lm': 0, 'lj': 0, 'lk': 1, 'lh': 6, 'li': 13, 'lv': 0, 'lw': 0, 'lt': 2, 'lu': 0, 'lr': 11, 'ls': 10, 'lp': 5, 'lq': 0, 'lz': 0, 'lx': 0, 'ly': 0, 'wq': 0, 'yh': 7, 'yk': 0, 'yj': 0, 'ym': 2, 'yl': 0, 'yo': 6, 'yn': 0, 'ya': 0, 'yc': 2, 'yb': 0, 'ye': 15, 'yd': 0, 'yg': 1, 'yf': 0, 'yy': 0, 'yx': 1, 'yz': 0, 'yq': 0, 'yp': 1, 'ys': 36, 'yr': 7, 'yu': 5, 'yt': 8, 'yw': 0, 'yv': 0, 'em': 0, 'el': 3, 'eo': 93, 'en': 5, 'ei': 89, 'eh': 0, 'ek': 0, 'ej': 0, 'ee': 0, 'ed': 11, 'eg': 2, 'ef': 2, 'ea': 388, 'ec': 3, 'eb': 0, 'ey': 18, 'ex': 0, 'ez': 0, 'eu': 15, 'et': 6, 'ew': 1, 'ev': 0, 'eq': 0, 'ep': 0, 'es': 12, 'er': 14, 'rt': 22, 'ru': 4, 'rv': 0, 'rw': 0, 'rp': 14, 'rq': 0, 'rr': 0, 'rs': 12, 'rx': 1, 'ry': 0, 'rz': 0, 'rd': 30, 're': 12, 'rf': 2, 'rg': 2, 'ra': 0, 'rb': 14, 'rc': 0, 'rl': 8, 'rm': 4, 'rn': 20, 'ro': 1, 'rh': 8, 'ri': 2, 'rj': 0, 'rk': 5, 'xj': 0, 'xk': 0, 'xh': 0, 'xi': 0, 'xn': 0, 'xo': 0, 'xl': 0, 'xm': 0, 'xb': 0, 'xc': 0, 'xa': 0, 'xf': 0, 'xg': 0, 'xd': 2, 'xe': 0, 'xz': 0, 'xx': 0, 'xy': 0, 'xr': 0, 'xs': 9, 'xp': 0, 'xq': 0, 'xv': 0, 'xw': 0, 'xt': 0, 'xu': 0, 'wy': 0, 'wx': 0, 'kc': 8, 'kb': 2, 'ka': 1, 'kg': 2, 'kf': 1, 'ke': 1, 'kd': 4, 'kk': 0, 'kj': 0, 'ki': 0, 'kh': 5, 'ko': 2, 'kn': 0, 'km': 5, 'kl': 0, 'ks': 6, 'kr': 0, 'kq': 0, 'kp': 0, 'kw': 4, 'kv': 0, 'ku': 0, 'kt': 0, 'kz': 3, 'ky': 0, 'kx': 0, 'dn': 3, 'do': 0, 'dl': 3, 'dm': 7, 'dj': 0, 'dk': 2, 'dh': 5, 'di': 0, 'df': 0, 'dg': 5, 'dd': 0, 'de': 12, 'db': 10, 'dc': 13, 'da': 1, 'dz': 0, 'dx': 0, 'dy': 2, 'dv': 0, 'dw': 4, 'dt': 22, 'du': 0, 'dr': 43, 'ds': 30, 'dp': 1, 'dq': 0, 'qq': 0, 'qp': 0, 'qs': 0, 'qr': 0, 'qu': 0, 'qt': 0, 'qw': 0, 'qv': 0, 'qy': 0, 'qx': 0, 'qz': 0, 'qa': 0, 'qc': 1, 'qb': 0, 'qe': 0, 'qd': 0, 'qg': 27, 'qf': 0, 'qi': 0, 'qh': 0, 'qk': 0, 'qj': 0, 'qm': 0, 'ql': 0, 'qo': 0, 'qn': 0, 'wc': 1, 'wb': 2, 'wa': 2, 'wo': 0, 'wn': 0, 'wm': 0, 'wg': 0, 'wf': 0, 'we': 1, 'wd': 0, 'jx': 0, 'jy': 0, 'jz': 0, 'jt': 0, 'ju': 0, 'jv': 0, 'jw': 0, 'jp': 0, 'jq': 0, 'jr': 0, 'js': 5, 'jl': 2, 'jm': 1, 'jn': 0, 'jo': 0, 'jh': 0, 'ji': 0, 'jj': 0, 'jk': 0, 'jd': 9, 'je': 0, 'jf': 0, 'jg': 1, 'ja': 0, 'jb': 1, 'jc': 1, 'ww': 0, 'wv': 0, 'wu': 1, 'wt': 3, 'ws': 3, 'wr': 6, 'ck': 1, 'cj': 0, 'ci': 0, 'ch': 0, 'co': 1, 'cn': 9, 'cm': 7, 'cl': 0, 'cc': 0, 'cb': 5, 'ca': 6, 'wp': 7, 'cg': 5, 'cf': 9, 'ce': 0, 'cd': 16, 'cz': 0, 'cy': 1, 'cx': 1, 'cs': 39, 'cr': 5, 'cq': 2, 'cp': 10, 'cw': 7, 'cv': 3, 'cu': 1, 'ct': 40, 'pr': 1, 'ps': 3, 'pp': 0, 'pq': 0, 'pv': 4, 'pw': 1, 'pt': 6, 'pu': 0, 'pz': 0, 'px': 0, 'py': 0, 'wz': 0, 'pb': 11, 'pc': 1, 'pa': 0, 'pf': 6, 'pg': 5, 'pd': 2, 'pe': 0, 'pj': 9, 'pk': 0, 'ph': 0, 'pi': 2, 'pn': 6, 'po': 15, 'pl': 2, 'pm': 7, 'iy': 15, 'ix': 1, 'vb': 0, 'iz': 0, 'vd': 0, 've': 0, 'vf': 3, 'vg': 0, 'iq': 0, 'ip': 0, 'is': 2, 'ir': 0, 'iu': 47, 'it': 1, 'iw': 2, 'iv': 0, 'ii': 0, 'ih': 0, 'ik': 0, 'ij': 0, 'im': 0, 'il': 6, 'io': 49, 'in': 0, 'ia': 103, 'vy': 0, 'ic': 0, 'ib': 0, 'ie': 146, 'id': 0, 'ig': 1, 'if': 0, 'wh': 2, 'yi': 15, 'vr': 0, 'vs': 8, 'bd': 9, 'be': 2, 'bf': 2, 'bg': 3, 'ba': 0, 'bb': 0, 'bc': 9, 'bl': 5, 'bm': 11, 'bn': 5, 'bo': 0, 'bh': 1, 'bi': 0, 'bj': 0, 'bk': 0, 'bt': 1, 'bu': 0, 'bv': 0, 'bw': 8, 'bp': 10, 'bq': 0, 'br': 0, 'bs': 2, 'bx': 0, 'by': 0, 'bz': 0, 'oo': 0, 'on': 0, 'om': 0, 'ol': 0, 'ok': 2, 'oj': 0, 'oi': 25, 'oh': 0, 'og': 0, 'of': 0, 'oe': 116, 'od': 3, 'oc': 1, 'ob': 1, 'oa': 91, 'oz': 0, 'oy': 18, 'ox': 0, 'ow': 0, 'ov': 0, 'ou': 39, 'ot': 14, 'os': 4, 'or': 2, 'oq': 0, 'op': 14, 'hz': 0, 'hx': 0, 'hy': 0, 'hr': 3, 'hs': 1, 'hp': 3, 'hq': 0, 'hv': 0, 'hw': 2, 'ht': 11, 'hu': 0, 'hj': 0, 'hk': 2, 'hh': 0, 'hi': 0, 'hn': 14, 'ho': 2, 'hl': 0, 'hm': 12, 'hb': 8, 'hc': 0, 'ha': 1, 'hf': 0, 'hg': 0, 'hd': 3, 'he': 0, 'uy': 8, 'ux': 0, 'uz': 0, 'uu': 0, 'ut': 0, 'uw': 2, 'uv': 0, 'uq': 0, 'up': 0, 'us': 0, 'ur': 4, 'um': 0, 'ul': 0, 'uo': 43, 'un': 2, 'ui': 64, 'uh': 0, 'uk': 0, 'uj': 0, 'ue': 44, 'ud': 0, 'ug': 0, 'uf': 0, 'ua': 20, 'uc': 0, 'ub': 0, 'aa': 0, 'ac': 7, 'ab': 0, 'ae': 342, 'ad': 1, 'ag': 0, 'af': 0, 'ai': 118, 'ah': 2, 'ak': 1, 'aj': 0, 'am': 0, 'al': 0, 'ao': 76, 'an': 3, 'aq': 0, 'ap': 0, 'as': 35, 'ar': 1, 'au': 9, 'at': 9, 'aw': 1, 'av': 0, 'ay': 5, 'ax': 0, 'az': 0, 'nh': 19, 'ni': 1, 'nj': 0, 'nk': 4, 'nl': 35, 'nm': 78, 'nn': 0, 'no': 0, 'na': 2, 'nb': 7, 'nc': 6, 'nd': 5, 'ne': 3, 'nf': 0, 'ng': 1, 'nx': 2, 'ny': 0, 'nz': 2, 'np': 7, 'nq': 0, 'nr': 28, 'ns': 5, 'nt': 7, 'nu': 0, 'nv': 0, 'nw': 1, 'vp': 0, 'vq': 0},
                                 'transposition': {'gw': 0, 'gv': 0, 'gu': 3, 'gt': 0, 'gs': 0, 'gr': 3, 'gq': 0, 'gp': 0, 'gz': 0, 'gy': 0, 'gx': 0, 'gg': 0, 'gf': 0, 'ge': 2, 'gd': 0, 'gc': 0, 'gb': 0, 'ga': 4, 'go': 0, 'gn': 15, 'gm': 0, 'gl': 1, 'gk': 0, 'gj': 0, 'gi': 0, 'gh': 0, 'tz': 0, 'tx': 0, 'ty': 0, 'tv': 0, 'tw': 2, 'tt': 0, 'tu': 11, 'tr': 5, 'ts': 0, 'tp': 0, 'tq': 0, 'tn': 0, 'to': 3, 'tl': 4, 'tm': 0, 'tj': 0, 'tk': 0, 'th': 21, 'ti': 49, 'tf': 0, 'tg': 0, 'td': 0, 'te': 4, 'tb': 0, 'tc': 3, 'ta': 4, 'vu': 0, 'zl': 0, 'zm': 0, 'zn': 0, 'zo': 0, 'zh': 0, 'zi': 0, 'zj': 0, 'zk': 0, 'zd': 0, 'ze': 0, 'zf': 0, 'zg': 0, 'za': 0, 'zb': 0, 'zc': 0, 'zx': 0, 'zy': 0, 'zz': 0, 'zt': 0, 'zu': 0, 'zv': 0, 'zw': 0, 'zp': 0, 'zq': 0, 'zr': 0, 'zs': 0, 'wl': 0, 'va': 0, 'vc': 0, 'wk': 0, 'vh': 0, 'wj': 0, 'vi': 4, 'vj': 0, 'vk': 0, 'vl': 0, 'vm': 0, 'wi': 0, 'vn': 0, 'vo': 0, 'me': 20, 'md': 0, 'mg': 0, 'mf': 0, 'ma': 9, 'mc': 0, 'mb': 0, 'mm': 0, 'ml': 0, 'mo': 0, 'mn': 2, 'mi': 0, 'mh': 0, 'mk': 0, 'mj': 0, 'mu': 4, 'mt': 0, 'mw': 0, 'mv': 0, 'mq': 0, 'mp': 0, 'ms': 0, 'mr': 0, 'vt': 0, 'my': 0, 'mx': 0, 'mz': 0, 'vv': 0, 'vw': 0, 'vx': 0, 'vz': 0, 'fp': 0, 'fq': 0, 'fr': 0, 'fs': 0, 'ft': 0, 'fu': 0, 'fv': 0, 'fw': 0, 'fx': 0, 'fy': 0, 'fz': 0, 'fa': 0, 'fb': 0, 'fc': 0, 'fd': 0, 'fe': 0, 'ff': 0, 'fg': 0, 'fh': 0, 'fi': 12, 'fj': 0, 'fk': 0, 'fl': 1, 'fm': 0, 'fn': 0, 'fo': 0, 'sz': 0, 'sy': 16, 'sx': 0, 'ss': 0, 'sr': 0, 'sq': 0, 'sp': 22, 'sw': 0, 'sv': 0, 'su': 3, 'st': 1, 'sk': 0, 'sj': 0, 'si': 15, 'sh': 5, 'so': 1, 'sn': 0, 'sm': 2, 'sl': 5, 'sc': 0, 'sb': 0, 'sa': 4, 'sg': 0, 'sf': 0, 'se': 9, 'sd': 0, 'lf': 0, 'lg': 1, 'ld': 12, 'le': 20, 'lb': 0, 'lc': 0, 'la': 11, 'ln': 0, 'lo': 1, 'll': 0, 'lm': 0, 'lj': 0, 'lk': 0, 'lh': 0, 'li': 4, 'lv': 9, 'lw': 0, 'lt': 1, 'lu': 3, 'lr': 0, 'ls': 1, 'lp': 3, 'lq': 0, 'lz': 0, 'lx': 0, 'ly': 7, 'wq': 0, 'yh': 0, 'yk': 0, 'yj': 0, 'ym': 0, 'yl': 3, 'yo': 0, 'yn': 0, 'ya': 0, 'yc': 2, 'yb': 1, 'ye': 0, 'yd': 0, 'yg': 1, 'yf': 0, 'yy': 0, 'yx': 0, 'yz': 0, 'yq': 0, 'yp': 2, 'ys': 10, 'yr': 1, 'yu': 0, 'yt': 0, 'yw': 0, 'yv': 0, 'em': 6, 'el': 21, 'eo': 11, 'en': 16, 'ei': 60, 'eh': 0, 'ek': 0, 'ej': 0, 'ee': 0, 'ed': 5, 'eg': 0, 'ef': 0, 'ea': 1, 'ec': 4, 'eb': 0, 'ey': 2, 'ex': 0, 'ez': 0, 'eu': 85, 'et': 0, 'ew': 0, 'ev': 0, 'eq': 0, 'ep': 2, 'es': 5, 'er': 29, 'rt': 2, 'ru': 10, 'rv': 0, 'rw': 0, 'rp': 1, 'rq': 0, 'rr': 0, 'rs': 0, 'rx': 0, 'ry': 2, 'rz': 0, 'rd': 0, 're': 24, 'rf': 0, 'rg': 3, 'ra': 12, 'rb': 0, 'rc': 0, 'rl': 2, 'rm': 0, 'rn': 7, 'ro': 30, 'rh': 0, 'ri': 14, 'rj': 0, 'rk': 2, 'xj': 0, 'xk': 0, 'xh': 0, 'xi': 0, 'xn': 0, 'xo': 0, 'xl': 0, 'xm': 0, 'xb': 0, 'xc': 0, 'xa': 0, 'xf': 0, 'xg': 0, 'xd': 0, 'xe': 0, 'xz': 0, 'xx': 0, 'xy': 0, 'xr': 0, 'xs': 0, 'xp': 1, 'xq': 0, 'xv': 0, 'xw': 0, 'xt': 0, 'xu': 0, 'wy': 8, 'wx': 0, 'kc': 0, 'kb': 0, 'ka': 0, 'kg': 0, 'kf': 0, 'ke': 2, 'kd': 0, 'kk': 0, 'kj': 0, 'ki': 0, 'kh': 0, 'ko': 0, 'kn': 0, 'km': 0, 'kl': 0, 'ks': 0, 'kr': 0, 'kq': 0, 'kp': 0, 'kw': 0, 'kv': 0, 'ku': 0, 'kt': 0, 'kz': 0, 'ky': 0, 'kx': 0, 'dn': 0, 'do': 0, 'dl': 0, 'dm': 0, 'dj': 0, 'dk': 0, 'dh': 0, 'di': 7, 'df': 0, 'dg': 0, 'dd': 0, 'de': 0, 'db': 0, 'dc': 0, 'da': 0, 'dz': 0, 'dx': 0, 'dy': 0, 'dv': 0, 'dw': 0, 'dt': 0, 'du': 2, 'dr': 1, 'ds': 0, 'dp': 0, 'dq': 0, 'qq': 0, 'qp': 0, 'qs': 0, 'qr': 0, 'qu': 0, 'qt': 0, 'qw': 0, 'qv': 0, 'qy': 0, 'qx': 0, 'qz': 0, 'qa': 0, 'qc': 0, 'qb': 0, 'qe': 0, 'qd': 0, 'qg': 0, 'qf': 0, 'qi': 0, 'qh': 0, 'qk': 0, 'qj': 0, 'qm': 0, 'ql': 0, 'qo': 0, 'qn': 0, 'wc': 0, 'wb': 0, 'wa': 0, 'wo': 1, 'wn': 1, 'wm': 1, 'wg': 0, 'wf': 0, 'we': 0, 'wd': 0, 'jx': 0, 'jy': 0, 'jz': 0, 'jt': 0, 'ju': 0, 'jv': 0, 'jw': 0, 'jp': 0, 'jq': 0, 'jr': 0, 'js': 0, 'jl': 0, 'jm': 0, 'jn': 0, 'jo': 0, 'jh': 0, 'ji': 0, 'jj': 0, 'jk': 0, 'jd': 0, 'je': 0, 'jf': 0, 'jg': 0, 'ja': 0, 'jb': 0, 'jc': 0, 'ww': 0, 'wv': 0, 'wu': 0, 'wt': 0, 'ws': 0, 'wr': 0, 'ck': 0, 'cj': 0, 'ci': 85, 'ch': 1, 'co': 13, 'cn': 0, 'cm': 0, 'cl': 15, 'cc': 0, 'cb': 0, 'ca': 0, 'wp': 0, 'cg': 0, 'cf': 0, 'ce': 1, 'cd': 0, 'cz': 0, 'cy': 0, 'cx': 0, 'cs': 3, 'cr': 0, 'cq': 0, 'cp': 0, 'cw': 0, 'cv': 0, 'cu': 7, 'ct': 0, 'pr': 5, 'ps': 3, 'pp': 0, 'pq': 0, 'pv': 0, 'pw': 0, 'pt': 6, 'pu': 0, 'pz': 0, 'px': 0, 'py': 0, 'wz': 0, 'pb': 0, 'pc': 0, 'pa': 17, 'pf': 0, 'pg': 0, 'pd': 0, 'pe': 4, 'pj': 0, 'pk': 0, 'ph': 1, 'pi': 0, 'pn': 0, 'po': 1, 'pl': 0, 'pm': 0, 'iy': 0, 'ix': 0, 'vb': 0, 'iz': 3, 'vd': 0, 've': 1, 'vf': 0, 'vg': 0, 'iq': 1, 'ip': 0, 'is': 42, 'ir': 13, 'iu': 0, 'it': 35, 'iw': 0, 'iv': 6, 'ii': 0, 'ih': 0, 'ik': 0, 'ij': 0, 'im': 0, 'il': 9, 'io': 11, 'in': 5, 'ia': 15, 'vy': 0, 'ic': 31, 'ib': 8, 'ie': 66, 'id': 3, 'ig': 3, 'if': 1, 'wh': 4, 'yi': 0, 'vr': 0, 'vs': 0, 'bd': 0, 'be': 2, 'bf': 0, 'bg': 0, 'ba': 0, 'bb': 0, 'bc': 0, 'bl': 1, 'bm': 1, 'bn': 0, 'bo': 2, 'bh': 0, 'bi': 0, 'bj': 0, 'bk': 0, 'bt': 0, 'bu': 0, 'bv': 0, 'bw': 0, 'bp': 0, 'bq': 0, 'br': 0, 'bs': 2, 'bx': 0, 'by': 0, 'bz': 0, 'oo': 0, 'on': 5, 'om': 0, 'ol': 1, 'ok': 0, 'oj': 0, 'oi': 5, 'oh': 0, 'og': 0, 'of': 0, 'oe': 4, 'od': 0, 'oc': 2, 'ob': 0, 'oa': 5, 'oz': 0, 'oy': 0, 'ox': 1, 'ow': 7, 'ov': 0, 'ou': 0, 'ot': 1, 'os': 1, 'or': 11, 'oq': 0, 'op': 1, 'hz': 0, 'hx': 0, 'hy': 0, 'hr': 0, 'hs': 0, 'hp': 0, 'hq': 0, 'hv': 0, 'hw': 0, 'ht': 10, 'hu': 0, 'hj': 0, 'hk': 0, 'hh': 0, 'hi': 0, 'hn': 0, 'ho': 0, 'hl': 0, 'hm': 0, 'hb': 0, 'hc': 0, 'ha': 12, 'hf': 0, 'hg': 0, 'hd': 0, 'he': 15, 'uy': 0, 'ux': 0, 'uz': 0, 'uu': 0, 'ut': 2, 'uw': 0, 'uv': 0, 'uq': 0, 'up': 2, 'us': 11, 'ur': 11, 'um': 1, 'ul': 2, 'uo': 20, 'un': 0, 'ui': 2, 'uh': 0, 'uk': 0, 'uj': 0, 'ue': 1, 'ud': 1, 'ug': 2, 'uf': 0, 'ua': 22, 'uc': 5, 'ub': 0, 'aa': 0, 'ac': 2, 'ab': 0, 'ae': 1, 'ad': 1, 'ag': 0, 'af': 0, 'ai': 19, 'ah': 0, 'ak': 1, 'aj': 0, 'am': 4, 'al': 14, 'ao': 10, 'an': 25, 'aq': 0, 'ap': 3, 'as': 3, 'ar': 27, 'au': 31, 'at': 5, 'aw': 0, 'av': 0, 'ay': 0, 'ax': 0, 'az': 0, 'nh': 0, 'ni': 1, 'nj': 0, 'nk': 0, 'nl': 0, 'nm': 3, 'nn': 0, 'no': 0, 'na': 15, 'nb': 0, 'nc': 6, 'nd': 2, 'ne': 12, 'nf': 0, 'ng': 8, 'nx': 0, 'ny': 0, 'nz': 0, 'np': 0, 'nq': 0, 'nr': 0, 'ns': 6, 'nt': 4, 'nu': 0, 'nv': 0, 'nw': 0, 'vp': 0, 'vq': 0}}

    def generate_edits1(self, token):
        """
        Generate all possible one-edit-away candidates for a given token.

        Parameters:
        -----------
        token : str
            The token for which to generate candidate corrections.

        Returns:
        --------
        edit1_candidates : dict
            A dictionary mapping candidate corrections (one edit away) to their probabilities.
            The probability represents the multiplication of the error probability by the probability of appearing in the text: p(x|w)*p(w).
        """
        edit1_candidates = {}  # A dictionary to hold the candidates and their corresponding probability
        english_alphabet = 'abcdefghijklmnopqrstuvwxyz'
        token_splits = [(token[:i], token[i:]) for i in range(len(token) + 1)]  # All token splits
        num_of_unigrams = len(self.lm.unigram_char_dict)
        num_of_bigrams = len(self.lm.bigram_char_dict)

        # Case 1: Deletion error
        # E.g.: Error token is 'del_tion', Correction token is 'deletion'
        for idx, (L, R) in enumerate(token_splits):
            for char in english_alphabet:
                curr_candidate = L + char + R
                if L:
                    curr_bigram = L[-1] + char
                    if curr_bigram not in self.error_tables['deletion']:
                        continue
                    curr_proba = (self.error_tables['deletion'][curr_bigram] + 1) / (self.lm.bigram_char_dict.get(curr_bigram, 1E15) + num_of_bigrams)
                else:
                    if '#' + char not in self.error_tables['deletion']:
                        continue
                    curr_proba = (self.error_tables['deletion']['#' + char] + 1) / (self.lm.bigram_char_dict.get(' ' + char, 1E15) + num_of_bigrams)
                edit1_candidates[curr_candidate] = edit1_candidates.get(curr_candidate, 0) + curr_proba  # Sum of the probabilities

        # Case 2: Insertion error
        # E.g.: Error token is 'ipnsertion', Correction token is 'insertion'
        for idx, (L, R) in enumerate(token_splits):
            if R:
                curr_candidate = L + R[1:]
                if L:
                    curr_unigram = L[-1]
                    if curr_unigram + R[0] not in self.error_tables['insertion']:
                        continue
                    curr_proba = (self.error_tables['insertion'][curr_unigram + R[0]] + 1) / (self.lm.unigram_char_dict.get(curr_unigram, 1E15) + num_of_unigrams)
                else:
                    if '#' + R[0] not in self.error_tables['insertion']:
                        continue
                    curr_proba = (self.error_tables['insertion']['#' + R[0]] + 1) / (self.lm.unigram_char_dict.get(' ', 1E15) + num_of_unigrams)
                edit1_candidates[curr_candidate] = edit1_candidates.get(curr_candidate, 0) + curr_proba

        # Case 3: Substitution error
        # E.g.: Error token is 'substituxion', Correction token is 'substitution'
        for idx, (L, R) in enumerate(token_splits):
            for char in english_alphabet:
                curr_candidate = L + char + R[1:]
                if R:
                    curr_unigram = R[0]
                    if curr_unigram + char not in self.error_tables['substitution']:
                        continue
                    curr_proba = (self.error_tables['substitution'][curr_unigram + char] + 1) / (self.lm.unigram_char_dict.get(curr_unigram, 1E15) + num_of_unigrams)
                    edit1_candidates[curr_candidate] = edit1_candidates.get(curr_candidate, 0) + curr_proba

        # Case 4: Transposition error
        # E.g.: Error token is 'rtansposition', Correction token is 'transposition'
        for idx, (L, R) in enumerate(token_splits):
            if len(R) > 1:
                curr_bigram = R[0] + R[1]
                curr_candidate = L + R[1] + R[0] + R[2:]
                if curr_bigram not in self.error_tables['transposition']:
                    continue
                curr_proba = (self.error_tables['transposition'][curr_bigram] + 1) / (self.lm.bigram_char_dict.get(curr_bigram, 1E15) + num_of_bigrams)
                edit1_candidates[curr_candidate] = edit1_candidates.get(curr_candidate, 0) + curr_proba

        return edit1_candidates

    def generate_edits2(self, edit1_cands):
        """
        Generate candidates that are two edits away from the original token.

        Parameters:
        -----------
        edit1_cands : dict
            Dictionary of one-edit-away candidates.

        Returns:
        --------
        edit2_candidates : dict
            A dictionary mapping candidates (two edits away) to their probabilities.
        """
        edit2_candidates = {}
        edit1_cands = list(edit1_cands.items())

        for edit1_cand in edit1_cands:
            curr_edit2_cands = self.generate_edits1(edit1_cand[0])  # Apply edits1 again to generate candidates for edits2
            edit1_proba = edit1_cand[1]
            curr_edit2_cands = {edit2_cand: edit1_proba * edit2_proba if edit1_proba != 0 else edit2_proba for edit2_cand, edit2_proba in curr_edit2_cands.items()}
            for edit2_cand, edit2_proba in curr_edit2_cands.items():
                edit2_candidates[edit2_cand] = edit2_candidates.get(edit2_cand, 0) + edit2_proba  # Insert the updated probabilities for each candidate

        return edit2_candidates

    def find_known_tokens(self, tokens):
        """
        Find tokens that are known (i.e., appear in the language model's dictionary).

        Parameters:
        -----------
        tokens : dict
            A dictionary of candidates with their probabilities.

        Returns:
        --------
        known_tokens : set
            A set of known tokens that appear in the language model's dictionary.
        """
        return set(token for token in tokens if token in self.lm.token2tf_dict)

    def generate_possible_edits(self, token):
        """
        Generate all possible candidates for correcting a token, considering up to two edits.

        Parameters:
        -----------
        token : str
            The token for which to generate possible corrections.

        Returns:
        --------
        candidates : set
            A set of possible candidates for correcting the token.
        """
        candidates = set()
        self.possible_edits = {}  # Re-initializing the candidate dictionary for each token tested

        # Find possible candidates after performing edits1 and edits2
        edits1 = self.generate_edits1(token)
        edits2 = self.generate_edits2(edits1)

        # Populate the candidate dictionary with the sum of the probabilities for each edit
        for candidate, proba in edits1.items():
            self.possible_edits[candidate] = self.possible_edits.get(candidate, 0) + proba
        for candidate, proba in edits2.items():
            self.possible_edits[candidate] = self.possible_edits.get(candidate, 0) + proba

        candidates.update(self.find_known_tokens(self.possible_edits))

        return candidates

    def generate_possible_edits_with_probabilities(self, token, alpha):
        """
        Generate possible correction candidates and their associated probabilities.

        Parameters:
        -----------
        token : str
            The token for which to generate corrections.
        alpha : float
            The probability of retaining the original token.

        Returns:
        --------
        final_cand_proba_list : list
            A list of tuples, each containing a candidate and its probability.
        """
        final_cand_proba_list = []
        candidates = self.generate_possible_edits(token)  # Generate possible edits for the given token
        cand_proba_list = [(cand, self.possible_edits[cand]) for cand in candidates]  # Create a list of candidates with their corresponding probabilities
        total = sum(proba for _, proba in cand_proba_list)  # Calculate the total probability to normalize candidate weights
        norm_cand_proba_list = [(cand, proba / total) for cand, proba in cand_proba_list]  # Normalize the probabilities

        # Distribute the probabilities, assigning 'alpha' to the original token
        for cand, proba in norm_cand_proba_list:
            if cand == token:
                final_cand_proba_list.append((cand, alpha))
            else:
                final_cand_proba_list.append((cand, (1 - alpha) * proba))

        return final_cand_proba_list

    def simple_noisy_channel(self, contextless_tokens, rest_of_tokens, alpha=0.95):
        """
        Apply the Noisy Channel model for short texts, treating each token independently.

        Parameters:
        -----------
        contextless_tokens : list of str
            The tokens to be spell-checked.
        rest_of_tokens : list of str
            The remaining tokens in the text (used for context).
        alpha : float, optional
            The probability of keeping a token unchanged (default is 0.95).

        Returns:
        --------
        corrected_sentences : list of str
            A list of corrected sentences, each being a possible candidate.
        """
        sentence_corrections = []
        total_tokens = sum(self.lm.token2tf_dict.values())  # The total amount of tokens in the text
        vocabulary_size = self.lm.vocabulary_size  # The amount of unique tokens in the text

        for i, token in enumerate(contextless_tokens):
            final_cand_proba_list = []
            cand_proba_list = self.generate_possible_edits_with_probabilities(token, alpha)  # Generate possible edits and their probabilities
            # Compute final candidate probabilities with Laplace smoothing
            for cand, proba in cand_proba_list:
                cand_prior_proba = (self.lm.token2tf_dict.get(cand, 0) + 1) / (total_tokens + vocabulary_size)  # Laplace smoothing
                final_cand_proba_list.append((cand, proba * cand_prior_proba))

            # Select the candidate with the maximum probability
            if final_cand_proba_list:  # Check if there are possible candidates
                fixed_token = max(final_cand_proba_list, key=lambda x: x[1])[0]
            else:
                fixed_token = token

            # Create the corrected sentence
            corrected_sentence = contextless_tokens[:i] + [fixed_token] + contextless_tokens[i + 1:] + rest_of_tokens
            sentence_corrections.append(' '.join(corrected_sentence))

        return sentence_corrections

    def context_sensitive_noisy_channel(self, tokens, window_size=3, alpha=0.95):
        """
        Apply the Noisy Channel model for long texts, considering token context within a window.

        Parameters:
        -----------
        tokens : list of str
            The tokens to be spell-checked.
        window_size : int, optional
            The size of the context window (default is 3).
        alpha : float, optional
            The probability of keeping a token unchanged (default is 0.95).

        Returns:
        --------
        corrected_sentences : list of str
            A list of corrected sentences, each being a possible candidate.
        """
        # Implement the context-sensitive noisy channel model for longer texts
        tokens_with_context = []  # A list of n-grams of a token and its context
        corrected_sentences = []

        for i in range(len(tokens) - window_size + 1):
            tokens_with_context.append(tokens[i:i + window_size])

        for i, ngram in enumerate(tokens_with_context):
            final_cand_proba_list = []
            cand_proba_list = self.generate_possible_edits_with_probabilities(ngram[-1], alpha)  # Generate possible edits and their probabilities
            for cand, proba in cand_proba_list:
                ngram_correction = ' '.join(ngram[:-1] + [cand])
                final_cand_proba_list.append((cand, proba * self.lm.smooth(ngram_correction)))

            # Select the candidate with the maximum probability
            if final_cand_proba_list:  # Check if there are possible candidates
                fixed_token = max(final_cand_proba_list, key=lambda x: x[1])[0]
            else:
                fixed_token = ngram[-1]

            # Create the corrected sentence
            corrected_sentence = tokens[:i + window_size - 1] + [fixed_token] + tokens[i + window_size:]
            corrected_sentences.append(' '.join(corrected_sentence))

        return corrected_sentences

    def spell_check(self, text, alpha=0.95):
        """
        Find the most probable fix for the specified text.
        Use a simple noisy channel model if the number of tokens in the specified text is smaller than the length (n) of the language model.

        Parameters:
        -----------
        text : str
            The input text to be spell-checked.
        alpha : float, optional
            The probability of keeping a token unchanged (default is 0.95).

        Returns:
        --------
        selected_sentence_correction : str
            The most probable corrected version of the input text.
        """
        self.possible_edits = {}  # Re-initializing the candidate dictionary for each token tested
        text = normalize_text(text)  # Normalize the text
        tokens = text.split()  # Text tokenization
        window_size = self.lm.get_model_window_size()  # Get the language model's window size

        # Simple Noisy Channel
        if len(tokens) < window_size:
            sentence_corrections = self.simple_noisy_channel(tokens, [], alpha)  # All possible sentence corrections
        # Context Sensitive Noisy Channel
        else:
            contextless_tokens = tokens[:window_size - 1]
            rest_of_tokens = tokens[window_size - 1:]
            simple_sentence_corrections = self.simple_noisy_channel(contextless_tokens, rest_of_tokens, alpha)
            context_sentence_corrections = self.context_sensitive_noisy_channel(tokens, window_size, alpha)
            sentence_corrections = simple_sentence_corrections + context_sentence_corrections  # All possible sentence corrections

        if not sentence_corrections:
            return text  # Return the original text if there are no possible candidates

        # Evaluate and score each sentence correction
        sentence_correction_scores = [(sentence_correction, self.lm.evaluate_text(sentence_correction)) for sentence_correction in sentence_corrections]
        selected_sentence_correction = max(sentence_correction_scores, key=lambda x: x[1])[0]  # Select the sentence correction with the highest score

        return selected_sentence_correction

    def evaluate_text(self, text):
        """
        Evaluate the likelihood of a given text based on the language model.
        Smoothing is applied on texts containing OOV tokens.

        Parameters:
        -----------
        text : str
            The input text to evaluate.

        Returns:
        --------
        sentence_log_prob : float
            The log-likelihood score of the text.
        """
        if self.lm:
            return self.lm.evaluate_text(text)
        else:
            raise ValueError("Language model is not set.")


    #####################################################################
    #                   Inner class                                     #
    #####################################################################

    class LanguageModel:
        """
        A Markov Language Model for generating text and evaluating its likelihood.

        This class implements a Markov Language Model that learns from a given text corpus.
        It supports both word-level and character-level language generation, allowing the
        model to produce text based on learned n-grams and their frequencies. The model also
        provides methods for evaluating the likelihood of given text based on the learned probabilities,
         incorporating Laplace smoothing for better performance with unseen n-grams.
        """

        def __init__(self, n=3, chars=False):
            """
            Initialize the LanguageModel instance with specified n-gram length and token type.

            Parameters:
            -----------
            n : int, optional
                The length of the n-grams used in the model (default is 3).
            chars : bool, optional
                If True, the model uses character n-grams instead of word tokens (default is False).
            """
            self.n = n
            self.chars = chars
            self.model_dict = None  # A dictionary mapping n-grams to their counts
            self.token2tf_dict = None  # A dictionary mapping tokens to their term frequencies
            self.unigram_char_dict = None  # A dictionary for unigram character frequencies
            self.bigram_char_dict = None  # A dictionary for bi-gram character frequencies
            self.contexts = None  # A dictionary for context (n-1 grams) frequencies
            self.context_completions = None  # A dictionary for context completions and their frequencies
            self.vocabulary_size = None  # The count of unique tokens in the text

        def build_model(self, text):
            """
            Build the language model from the provided text.

            Parameters:
            -----------
            text : str
                The text corpus from which to construct the model.
            """
            n = self.n
            norm_text = normalize_text(text)  # A normalized version of the specified text
            self.build_frequency_dictionaries(norm_text)  # Build frequency dictionaries and calculate vocabulary size
            self.model_dict = {}
            self.contexts = {}
            self.context_completions = defaultdict(lambda: defaultdict(int))

            tokens = list(text) if self.chars else text.split()  # Tokens can be ngrams of characters or ngrams of words
            # Build n-gram and context dictionaries
            for i in range(len(tokens) - n + 1):
                if self.chars:
                    ngram = ''.join(tokens[i:i + n])
                    prefix = ''.join(tokens[i:i + n - 1])  # n-1 grams
                    self.model_dict[ngram] = self.model_dict.get(ngram, 0) + 1
                    self.contexts[prefix] = self.contexts.get(prefix, 0) + 1
                    self.context_completions[prefix][tokens[i + self.n - 1]] += 1
                else:
                    ngram = ' '.join(tokens[i:i + n])
                    prefix = ' '.join(tokens[i:i + n - 1])  # n-1 grams
                    self.model_dict[ngram] = self.model_dict.get(ngram, 0) + 1
                    self.contexts[prefix] = self.contexts.get(prefix, 0) + 1
                    self.context_completions[prefix][tokens[i + self.n - 1]] += 1

        def build_frequency_dictionaries(self, text):
            """
            Create frequency dictionaries for tokens, uni-grams, and bi-grams.

            Parameters:
            -----------
            text : str
                The text to analyze for frequency counts.
            """
            # Build token2tf_dict and calculate vocabulary size
            self.token2tf_dict = Counter(re.findall(r'\w+', text))
            self.vocabulary_size = len(self.token2tf_dict)

            # Build unigram and bigram dicts
            text_chars = list(text)
            self.unigram_char_dict = {}
            self.bigram_char_dict = {}

            for i in range(len(text_chars) - 1):  # Iterate over all characters in the text, excluding the last one (for forming bi-grams)
                self.unigram_char_dict[text_chars[i]] = self.unigram_char_dict.get(text_chars[i], 0) + 1
                self.bigram_char_dict[''.join(text_chars[i:i + 2])] = self.bigram_char_dict.get(''.join(text_chars[i:i + 2]), 0) + 1
            self.unigram_char_dict[text_chars[-1]] = self.unigram_char_dict.get(text_chars[-1], 0) + 1  # Count the last uni-gram char

        def get_model_dictionary(self):
            """
            Retrieve the model's n-gram dictionary.

            Returns:
            --------
            dict
                The dictionary containing n-grams and their counts.
            """
            return self.model_dict

        def get_model_window_size(self):
            """
            Get the size of the context window used in the model.

            Returns:
            --------
            int
                The n value representing the n-gram size.
            """
            return self.n

        def generate(self, context=None, n=20):
            """
            Generate text of specified length based on a seed context.
            If no context is specified the context should be sampled from the models' contexts distribution.
            Generation should stop before the n'th word if the contexts are exhausted.
            If the length of the specified context exceeds (or equal to) the specified n, the method should return a prefix of length n of the specified context.

            Parameters:
            -----------
            context : str, optional
                A seed context to initiate text generation (default is None).
            n : int, optional
                The length of the text to generate (default is 20).

            Returns:
            --------
            str
                The generated text based on the language model.
            """
            if context:
                context = normalize_text(context)
                context_tokens = list(context) if self.chars else context.split()
            else:
                context_tokens = random.choice(list(self.contexts.keys())).split() if not self.chars else list(
                    random.choice(list(self.contexts.keys())))

            # If the length of the context exceeds or equals n, return the first n tokens of the context
            if len(context_tokens) >= n:
                return ' '.join(context_tokens[:n]) if not self.chars else ''.join(context_tokens[:n])

            generated_tokens = context_tokens[:]

            for _ in range(n - len(context_tokens)):
                # Form the current context based on the last (n-1) tokens
                current_context = ' '.join(generated_tokens[-(self.n - 1):]) if not self.chars else ''.join(
                    generated_tokens[-(self.n - 1):])

                # Collect all possible next tokens for the current context
                possible_next_tokens = {k.split()[-1]: v for k, v in self.model_dict.items() if
                                        k.startswith(current_context)} if not self.chars else {k[-1]: v for k, v in
                                                                                               self.model_dict.items()
                                                                                               if k.startswith(current_context)}

                if not possible_next_tokens:
                    # Fallback to a random word/character from the entire distribution if no suitable next word is found
                    possible_next_tokens = self.context_completions.get(random.choice(list(self.context_completions.keys())), None)
                    # If there are no possible next tokens, stop generating
                    if not possible_next_tokens:
                        break

                # Normalize the probabilities
                total_count = sum(possible_next_tokens.values())
                normalized_probs = {token: count / total_count for token, count in possible_next_tokens.items()}

                # Choose the next token based on the normalized probabilities
                next_token = random.choices(list(normalized_probs.keys()), list(normalized_probs.values()))[0]
                generated_tokens.append(next_token)

            return ' '.join(generated_tokens) if not self.chars else ''.join(generated_tokens)

        def evaluate_text(self, text):
            """
            Evaluate the log-likelihood of the specified text according to the model.
            Smoothing is applied on texts containing OOV tokens.

            Parameters:
            -----------
            text : str
                The text to evaluate for likelihood.

            Returns:
            --------
            float
                The log-likelihood of the text being generated by the model.
            """
            tokens = text.split()  # Text tokenization
            sentence_log_prob = 0
            window_size = self.get_model_window_size()
            total_tokens = sum(self.token2tf_dict.values())  # The total amount of tokens in the text
            vocabulary_size = self.vocabulary_size  # The amount of unique tokens in the text

            # Calculate the log prior probability with Laplace smoothing
            for token in tokens:
                # The multiplication of the priors of all the tokens in the corrected sentence
                # The sum of the logs is equal to the log of their multiplications
                sentence_log_prob += math.log((self.token2tf_dict.get(token, 0) + 1) / (total_tokens + vocabulary_size))

            # Add context probabilities when text length is greater than or equal to window size
            if len(tokens) >= window_size:
                for i in range(len(tokens) - window_size + 1):
                    ngram = ' '.join(tokens[i:i + window_size])
                    sentence_log_prob += math.log(self.smooth(ngram))

            if tokens:
                return sentence_log_prob / len(tokens)  # Normalize by the length of the text
            else:
                return float('-inf')  # Negative value for an empty string to prevent the model from selecting it

        def smooth(self, ngram):
            """
            Calculate the smoothed probability of the specified n-gram using Laplace smoothing.

            Parameters:
            -----------
            ngram : str
                The n-gram for which to compute the smoothed probability.

            Returns:
            --------
            float
                The smoothed probability of the n-gram.
            """
            context = ' '.join(ngram.split()[:-1])
            ngram_count = self.get_model_dictionary().get(ngram, 0)
            context_count = self.contexts.get(context, 0)
            num_of_ngrams = len(self.get_model_dictionary())

            # Laplace smoothing
            return (ngram_count + 1) / (context_count + num_of_ngrams)