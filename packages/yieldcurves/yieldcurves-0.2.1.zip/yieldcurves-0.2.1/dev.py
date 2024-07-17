from vectorizeit import vectorize
import pandas as pd
from businessdate import BusinessDate as bd, BusinessSchedule as bs, \
    BusinessRange as br, BusinessPeriod as bp
import plotly.express as px

from yieldcurves.tools import ascii_plot, lin
from yieldcurves.parametric import NelsonSiegelSvensson
from yieldcurves.datecurve import DateCurve
from yieldcurves import YieldCurve, Df
from yieldcurves.interpolation import linear

yc = YieldCurve(linear([1, 2, 3], [4, 5, 6]))
yc.update({4: 7})
dc = DateCurve(yc)
print(len(yc), yc(3.5), hasattr(dc, 'data'))

yc = YieldCurve(3)
print(len(yc), yc(3.5), hasattr(dc, 'data'))

exit()


today = bd()
dates = today + ['1y', '5y', '10y']
values = [0.01, 0.03, 0.02]

dc = DateCurve.from_interpolation(dates, values, origin=today.to_date())
print(dc, dc(today + '5y'), dc(bd() + '6y'), dc.domain)

exit()


yc = YieldCurve.from_short_rates(0.01)
print(yc, yc.swap(10))

df = YieldCurve.from_zero_rates(0.01, compounding_frequency=1)
print(Df(df))
print(df, df(10), df.df(10), Df(df)(10), df.swap(10))


NelsonSiegelSvensson.download()
d = NelsonSiegelSvensson._download
print(d)

x = lin(0, 30, 0.025)
f = NelsonSiegelSvensson.download(t=list(d.keys())[-1])
ascii_plot(x, f)

print(f(12))



exit()


f = NelsonSiegelSvensson(**_data)
p = SwapParRate(f)
y = lin(1., 10, 1.)
print(list(f(_) for _ in y))
print(list(p(_) for _ in y))
c = StrippedRateCurve(f, yield_curve=p, domain=y)
print(list(c(_) for _ in y))
print(list(c(_) for _ in y))


px.line(pd.DataFrame({
    'f': list(f(_) for _ in y),
    'p': list(p(_) for _ in y),
    'c': list(c(_) for _ in y),
})).show()

exit()


x = lin(0, 30, 0.025)
NelsonSiegelSvensson.download()
f = NelsonSiegelSvensson(date=-1)
g = NelsonSiegelSvensson(date='2020-01-03')

ascii_plot(x, f, g)

data = dict()
dates = NelsonSiegelSvensson.dates()
for i in range(len(dates) - 1 , len(dates) - 2500, -250):
    d = dates[i]
    data[d] = NelsonSiegelSvensson(date=d)(x)

df = pd.DataFrame(data)
df.index = x

import plotly.express as px
px.line(df).show()


exit()



@vectorize(keys=['number'])
def rnd(number, ndigits=13):
    return round(number, ndigits)


def lin(start, stop, step):
    r = [start]
    while r[-1] + step < stop:
        r.append(r[-1] + step)
    return r


class v:
    def __init__(self, *values):
        self._v = values

    def __call__(self, x):
        return (self._v * len(x))[:len(x)]


class YearFractionCurve:

    _int = lambda i: bp(days=i)
    _float = lambda f: bp(years=f)

    def __init__(self, curve):
        self.curve = curve

    def __call__(self, x):
        return self.curve.get_cash_rate(self._g(x))

    def _g(self, x):
        y = int(x)
        m = int((x - y) * 12)
        d = int(x - y - m / 12)
        one_day = bp(days=1)
        origin = self.curve.origin
        day_count = self.curve.day_count or _day_count
        y = origin + bp(years=y, months=m, days=d)
        while day_count(origin, y) < x:
            y += one_day
        while day_count(origin, y) >= x:
            y -= one_day
        return y

    def __str__(self):
        return str(self.curve)


today = bd()
domain = tuple(br(today, today + '1Y', '3M'))
periods = '1D', '2B', '8D', '2W', '14B', '1M', '1M1D', '3M', '6M', '6M2W1D', \
          '9M', '12M', '1Y', '2Y', '5Y', '5Y3M', '10Y', '30Y'# , '70Y'
#periods = '1D', '2B', '8D', '2W', '14B', '1M', '1M1D',
# rates = [0.02, 0.018, 0.015, 0.017]
rates = [0.02]
points = v(*rates)(domain)


A = dcf.CashRateCurve(domain, points, origin=today, forward_tenor='3M')
B = yc.CashRateCurve(domain, points, origin=today, forward_tenor='3M', frequency=4)

T = bd(20240406)
a = A.origin
b = B.origin
print(a, b, b - a)

a = A.day_count(A.origin, T)
b = _day_count(B.origin, T)
print(a, b, b - a)

a = A.get_discount_factor(T)
b = B.get_discount_factor(T)
print(a, b, b - a)
# exit()

for d in domain:
    for p in periods:
        _ = d + p
        a = A.get_zero_rate(_)
        b = B.get_zero_rate(_)
        print(_, a, b, rnd(a - b))

exit()


x = lin(0, 3, 3 / 100)
dcf_curve = YearFractionCurve(A)
yc_curve = YearFractionCurve(B)

ascii_plot(x, dcf_curve, yc_curve)
for _ in x:
    print(_, dcf_curve(_), rnd((yc_curve(_))))

exit()


x = lin(0, 10, 0.1)

z = init_curve(NelsonSiegelSvensson().download())
s = init_curve(NelsonSiegelSvensson().download())
s.curve.short_rate = True

# zz = Df2ZeroRate(ZeroRate2Df(z))
# zz = Df2ShortRate(ShortRate2Df(z))
# zz = Df2CashRate(CashRate2Df(z))
#
# diff = tuple(abs(z(xx) - zz(xx)) for xx in x)
# print(*rnd(diff))

#plot(x, z, Zero(s))
# exit()

c = CurveAlgebra(Cash(z, tenor=1))
ascii_plot(x, z, Cash(z, tenor=0.25), Cash(z, tenor=0.5), Cash(z, tenor=1))
# plot(x, z, Cash(z, tenor=0.25), Cash(z, tenor=0.5), Cash(z, tenor=1))


p = Price(z, 24)

ascii_plot(x, p)
# plot(x, p)


y = v(0.02, 0.018, 0.015, 0.017)(x)
l = linear(x, v(0.02)(x)) + 3

i = hz = linear(x, v(0.01, 0.02)(x))
# i = Intensity(z)
s = Prob(i)
pd = Pd(s)

today = bd()
domain = bs(today, '10y', '6m')
data = v(0.02, 0.018, 0.015, 0.017)(domain)


r = interp1d(domain, data, kind='quadratic')
r = linear(domain, data)

ascii_plot(x, r.curve)
# plot(x, r.curve)

print(*r.domain)
print(*rnd(r(r.domain), ndigits=8))


print(z['beta0'], z)

print(Df(0.04)(10))
print(Cv(0.04)(10))

print(*z.items())

z.plot()
