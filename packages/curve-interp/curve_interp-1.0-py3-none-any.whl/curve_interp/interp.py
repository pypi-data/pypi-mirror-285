import torch
import numpy as np


class PCHIP:
    def __init__(self, kx, ky):
        """
        :param kx: 1D Tensor, Must be the same length as the last dimension of y.
        :param ky: ND Tensor, The last dimension must be the actual y value to interpolate. (N, Length)
        """
        self.kx = kx
        self.ky = ky

    def __call__(self, t):
        """
        :param t: 1D Tensor, Must be the same length as the last dimension of y.
        :return: ND Tensor
        """
        return self.pchip(kx=self.kx, ky=self.ky, xv=t)

    def pchip(self, kx, ky, xv):
        n_dim = len(ky.shape)
        result = torch.empty((*ky.shape[: (n_dim - 1)], xv.shape[0]), device=ky.device)
        if n_dim > 1:
            if ((torch.numel(ky) / ky.shape[-1]) * xv.shape[0]) > 4194304:
                for i in range(result.shape[0]):
                    result[i] = self.pchip(kx, ky[i], xv)
                return result
        if kx.device.type == 'mps' or xv.device.type == 'mps':
            bucket = torch.bucketize(xv.to(device='cpu'), kx.to(device='cpu')) - 1
            bucket = bucket.to(device=kx.device)
        else:
            bucket = torch.bucketize(xv, kx) - 1
        bucket = torch.clamp(bucket, 0, kx.shape[0] - 2)
        tv_minus = (xv - kx[bucket]).unsqueeze(1)
        infer_tv = torch.cat((tv_minus ** 3, tv_minus ** 2, tv_minus,
                              torch.ones(tv_minus.shape, device=tv_minus.device)), 1)
        h = kx[1:] - kx[:-1]
        delta = (ky[..., 1:] - ky[..., :-1]) / h
        k = torch.sign(delta[..., :-1] * delta[..., 1:]) > 0
        w1 = 2 * h[1:] + h[:-1]
        w2 = h[1:] + 2 * h[:-1]
        whmean = (w1 / delta[..., :-1] + w2 / delta[..., 1:]) / (w1 + w2)
        slope = torch.zeros(ky.shape, device=ky.device)
        slope[..., 1:-1][k] = whmean[k].reciprocal()
        slope[..., 0] = ((2 * h[0] + h[1]) * delta[..., 0] - h[0] * delta[..., 1]) / (h[0] + h[1])
        slope_cond = torch.sign(slope[..., 0]) != torch.sign(delta[..., 0])
        slope[..., 0][slope_cond] = 0
        slope_cond = torch.logical_and(torch.sign(delta[..., 0]) != torch.sign(delta[..., 1]),
                                       torch.abs(slope[..., 0]) > torch.abs(3 * delta[..., 0]))
        slope[..., 0][slope_cond] = 3 * delta[..., 0][slope_cond]
        slope[..., -1] = ((2 * h[-1] + h[-2]) * delta[..., -1] - h[-1] * delta[..., -2]) / (h[-1] + h[-2])
        slope_cond = torch.sign(slope[..., -1]) != torch.sign(delta[..., -1])
        slope[..., -1][slope_cond] = 0
        slope_cond = torch.logical_and(torch.sign(delta[..., -1]) != torch.sign(delta[..., -1]),
                                       torch.abs(slope[..., -1]) > torch.abs(3 * delta[..., 1]))
        slope[..., -1][slope_cond] = 3 * delta[..., -1][slope_cond]
        t = (slope[..., :-1] + slope[..., 1:] - delta - delta) / h
        a = t / h
        b = (delta - slope[..., :-1]) / h - t
        py_coef = torch.stack((a, b, slope[..., :-1], ky[..., :-1]), -1)
        result = (py_coef[..., bucket, :] * infer_tv).sum(axis=-1)
        # result[:,0] = ky[:,0]
        # result[:,-1] = ky[:,-1]
        return result


class CubicSpline:
    def __init__(self, kx, ky):
        """
        :param kx: 1D Tensor, Must be the same length as the last dimension of y.
        :param ky: ND Tensor, The last dimension must be the actual y value to interpolate. (N, Length)
        """
        self._t, self._a, self._b, self._c, self._d = self.calc_coefficient(kx, ky)

    def __call__(self, t):
        """
        :param t: 1D Tensor, Must be the same length as the last dimension of y.
        :return: ND Tensor
        """
        max_len = self._b.size(-2) - 1
        index = torch.bucketize(t.detach(), self._t) - 1
        index = index.clamp(0, max_len)
        fractional = t - self._t[index]
        fractional = fractional.unsqueeze(-1)
        inner = self._c[..., index, :] + self._d[..., index, :] * fractional
        inner = self._b[..., index, :] + inner * fractional
        result = self._a[..., index, :] + inner * fractional
        return result.permute(1, 0)

    @staticmethod
    def _stack(tensors, dim):
        return tensors[0].unsqueeze(dim) if len(tensors) == 1 else torch.stach(tensors, dim=dim)

    @staticmethod
    def tri_diagonal(b, a_upper, a_diagonal, a_lower):
        a_upper, _ = torch.broadcast_tensors(a_upper, b[..., :-1])
        a_lower, _ = torch.broadcast_tensors(a_lower, b[..., :-1])
        a_diagonal, b = torch.broadcast_tensors(a_diagonal, b)
        channels = b.size(-1)
        new_b = np.empty(channels, dtype=object)
        new_a_diagonal = np.empty(channels, dtype=object)
        outs = np.empty(channels, dtype=object)
        new_b[0] = b[..., 0]
        new_a_diagonal[0] = a_diagonal[..., 0]
        for i in range(1, channels):
            w = a_lower[..., i - 1] / new_a_diagonal[i - 1]
            new_a_diagonal[i] = a_diagonal[..., i] - w * a_upper[..., i - 1]
            new_b[i] = b[..., i] - w * new_b[i - 1]
        outs[channels - 1] = new_b[channels - 1] / new_a_diagonal[channels - 1]
        for i in range(channels - 2, -1, -1):
            outs[i] = (new_b[i] - a_upper[..., i] * outs[i + 1]) / new_a_diagonal[i]
        return torch.stack(outs.tolist(), dim=-1)

    def _coefficient(self, t, x):
        length = x.size(-1)
        if length < 2:
            raise ValueError("Must have a time dimension of size at least 2.")
        elif length == 2:
            a = x[..., :1]
            b = (x[..., 1:] - x[..., :1]) / (t[..., 1:] - t[..., :1])
            two_c = torch.zeros(*x.shape[:-1], 1, dtype=x.dtype, device=x.device)
            three_d = torch.zeros(*x.shape[:-1], 1, dtype=x.dtype, device=x.device)
        else:
            time_diffs = t[1:] - t[:-1]
            time_diffs_reciprocal = time_diffs.reciprocal()
            time_diffs_reciprocal_squared = time_diffs_reciprocal ** 2
            three_path_diffs = 3 * (x[..., 1:] - x[..., :-1])
            six_path_diffs = 2 * three_path_diffs
            path_diffs_scaled = three_path_diffs * time_diffs_reciprocal_squared
            system_diagonal = torch.empty(length, dtype=x.dtype, device=x.device)
            system_diagonal[:-1] = time_diffs_reciprocal
            system_diagonal[-1] = 0
            system_diagonal[1:] += time_diffs_reciprocal
            system_diagonal *= 2
            system_rhs = torch.empty_like(x)
            system_rhs[..., :-1] = path_diffs_scaled
            system_rhs[..., -1] = 0
            system_rhs[..., 1:] += path_diffs_scaled
            knot_derivatives = self.tri_diagonal(system_rhs, time_diffs_reciprocal, system_diagonal,
                                                 time_diffs_reciprocal)
            a = x[..., :-1]
            b = knot_derivatives[..., :-1]
            two_c = (six_path_diffs * time_diffs_reciprocal
                     - 4 * knot_derivatives[..., :-1]
                     - 2 * knot_derivatives[..., 1:]) * time_diffs_reciprocal
            three_d = (-six_path_diffs * time_diffs_reciprocal
                       + 3 * (knot_derivatives[..., :-1]
                              + knot_derivatives[..., 1:])) * time_diffs_reciprocal_squared
        return a, b, two_c, three_d

    def _coefficient_missing_vals(self, t, x):
        if x.ndimension() == 1:
            return self._coefficient_missing_vals_scalar(t, x)
        else:
            a_pieces = []
            b_pieces = []
            two_c_pieces = []
            three_d_pieces = []
            for p in x.unbind(dim=0):
                a, b, two_c, three_d = self._coefficient_missing_vals(t, p)
                a_pieces.append(a)
                b_pieces.append(b)
                two_c_pieces.append(two_c)
                three_d_pieces.append(three_d)
            return (self._stack(a_pieces, dim=0),
                    self._stack(b_pieces, dim=0),
                    self._stack(two_c_pieces, dim=0),
                    self._stack(three_d_pieces, dim=0))

    def _coefficient_missing_vals_scalar(self, t, x):
        not_nan = ~torch.isnan(x)
        path_no_nan = x.masked_select(not_nan)
        if path_no_nan.size(0) == 0:
            return (torch.zeros(x.size(0) - 1, dtype=x.dtype, device=x.device),
                    torch.zeros(x.size(0) - 1, dtype=x.dtype, device=x.device),
                    torch.zeros(x.size(0) - 1, dtype=x.dtype, device=x.device),
                    torch.zeros(x.size(0) - 1, dtype=x.dtype, device=x.device))
        need_new_not_nan = False
        if torch.isnan(x[0]):
            if not need_new_not_nan:
                x = x.clone()
                need_new_not_nan = True
            x[0] = path_no_nan[0]
        if torch.isnan(x[-1]):
            if not need_new_not_nan:
                x = x.clone()
                need_new_not_nan = True
            x[-1] = path_no_nan[-1]
        if need_new_not_nan:
            not_nan = ~torch.isnan(x)
            path_no_nan = x.masked_select(not_nan)
        times_no_nan = t.masked_select(not_nan)

        (a_pieces_no_nan,
         b_pieces_no_nan,
         two_c_pieces_no_nan,
         three_d_pieces_no_nan) = self._coefficient(times_no_nan, path_no_nan)

        a_pieces = []
        b_pieces = []
        two_c_pieces = []
        three_d_pieces = []

        iter_times_no_nan = iter(times_no_nan)
        iter_coeffs_no_nan = iter(zip(a_pieces_no_nan, b_pieces_no_nan, two_c_pieces_no_nan, three_d_pieces_no_nan))
        next_time_no_nan = next(iter_times_no_nan)
        for time in t[:-1]:
            if time >= next_time_no_nan:
                prev_time_no_nan = next_time_no_nan
                next_time_no_nan = next(iter_times_no_nan)
                next_a_no_nan, next_b_no_nan, next_two_c_no_nan, next_three_d_no_nan = next(iter_coeffs_no_nan)
            offset = prev_time_no_nan - time
            a_inner = (0.5 * next_two_c_no_nan - next_three_d_no_nan * offset / 3) * offset
            a_pieces.append(next_a_no_nan + (a_inner - next_b_no_nan) * offset)
            b_pieces.append(next_b_no_nan + (next_three_d_no_nan * offset - next_two_c_no_nan) * offset)
            two_c_pieces.append(next_two_c_no_nan - 2 * next_three_d_no_nan * offset)
            three_d_pieces.append(next_three_d_no_nan)

        return (self._stack(a_pieces, dim=0),
                self._stack(b_pieces, dim=0),
                self._stack(two_c_pieces, dim=0),
                self._stack(three_d_pieces, dim=0))

    def calc_coefficient(self, kx, ky):
        ky = ky.permute(1, 0)
        if torch.isnan(ky).any():
            a, b, two_c, three_d = self._coefficient_missing_vals(kx, ky.transpose(-1, -2))
        else:
            a, b, two_c, three_d = self._coefficient(kx, ky.transpose(-1, -2))
        a = a.transpose(-1, -2)
        b = b.transpose(-1, -2)
        c = two_c.transpose(-1, -2) / 2
        d = three_d.transpose(-1, -2) / 3
        return kx, a, b, c, d
