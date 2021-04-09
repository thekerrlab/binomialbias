# def binomial_discrimination(n=9, ra=3,rbar=4):
'''
Code to supplement Objective Assessment of University Discrimination -
by Prof. P. A. Robinson, School of Physics, University of Sydney
Python conversion by Dr. C. C. Kerr, Institute for Disease Modeling

Input:
n - The total number of appointments
ra - Actual appointments of a group
rbar - Expected number of appointments expected given a fair process

Output:
CI - 95# Confidence interval for individuals given a fair process
cdfra - Cumulative distribution function of ra or less appointments
B - Preference ratio the estimate of the disparity in how two groups are viewed by selectors
U - Probability of unbiased selection numbers much less than 1 do imply bias and U < 0.1 should be cause for serious concern and U < 0.01 should provoke urgent action.

Example:
The below code will generate figure 1 of the paper
'''
n = 9; #40 possible appointments
rbar = 4; #An expected 50# of appointments
ra =3; #13 actual appointments were observed
#
#[CI,cdfra,B,U] = BinomialDiscrimination(n,ra,rbar)
##


#
f = rbar./n;
r = 0:n; #sampling
y = binopdf(r,n,f); #binomial distn
k = f*n;

#Calculation of the preference ratio
#(n-ra)./(n-rbar) - ratio for other group
#ra./rbar - ratio for relative proportion
B = ((n-ra)./(n-rbar))./(ra./rbar);


## First figure binomial distribution of expected appointments
subplot(2,1,1)

plot(r,y,'k','LineWidth',2.5);
hold on
xlim([0 n]);
ylabel('P_F(r)')
xlabel('r')

handle = gca;
handle.XMinorTick = 'on';
handle.YMinorTick = 'on';
handle.TickDir = 'out';
handle.TickLength = [.02 .02];
handle.Box = 'off';
handle.Color = 'none';
handle.FontSize = 14;
handle.YGrid = 'on';

## Calc cdf

plot([ra ra], [0 y(r==ra)],'r','LineWidth',2.5)

hold on

#Two conditions depending on whether group is >/< expected ratio, below adds the shading in fig1a

if ra <= k
area(r(r<=ra),y((r<=ra)),'FaceColor','r')
#ncdf = trapz(r(r<=ra),y((r<=ra))); #alternative calculation integral
#under curve
ncdf = sum(y((r<=ra)));


ncdfround = round(ncdf,2,'significant');

text(n/8+0.5,3*max(y)/4,['cdf(r_a) = ' num2str(ncdfround)],'Color','r','FontSize',14,'HorizontalAlignment','center')


else

   area(r(r>=ra),y((r>=ra)),'FaceColor','r')
#ncdf = trapz(r(r>=ra),y((r>=ra))); #alternative calculation integral
#under curve
ncdf = sum(y((r<=ra)));


ncdfround = round(ncdf,2,'significant');
text(3*n/4,3*max(y)/4,['cdf(r_a) = ' num2str(ncdfround)],'Color','r','FontSize',14,'HorizontalAlignment','center')


end

#Save cdf for output
cdfra = ncdfround;


#Add vertical line and r_a
plot([ra ra],[0.7*max(y)/4 0.7*max(y)/2],'r','LineWidth',2)
text(ra, 0.9*max(y)/2,'r_a' ,'Color','r','FontSize',14,'HorizontalAlignment','center')





## PLot 95# CI  values

#Gaussian CI approximation
bnpMean = n*f;
bnpSTD = sqrt(n*f*(1-f));


#3 std 99.7# CI
lowBnd2 = bnpMean-3*bnpSTD;
hiBnd2 = bnpMean+3*bnpSTD;

#2 std or 95# CI
lowBnd = bnpMean-2*bnpSTD;
hiBnd = bnpMean+2*bnpSTD;


# Ceil the lower bound of CI -- Integer value of individuals
lowBnd2 = ceil(lowBnd2);
lowBnd = ceil(lowBnd);

# Floor the upper bound of CI -- Integer value of individuals
hiBnd2 = floor(hiBnd2);
hiBnd = floor(hiBnd);

# Catching for values over/under -- we cannot have negative individuals or
# more than the population
if lowBnd2 < 0
    lowBnd2 = 0;
end

if lowBnd < 0
    lowBnd = 0;
end

if hiBnd2 > n
    hiBnd2 = n;
end

if hiBnd > n
    hiBnd = n;
end

# Now plot the CI lines

plot([lowBnd lowBnd], [0 y(r==lowBnd)],'b','LineWidth',2.5)
plot([hiBnd hiBnd], [0 y(r==hiBnd)],'b','LineWidth',2.5)

plot([lowBnd hiBnd], [1.1.*max(y) 1.1.*max(y)],'b','LineWidth',2.5)
scatter(k, 1.1.*max(y), 70, 'b','filled')
text(k,1.2.*max(y),'95# CI','Color','b','FontSize',14,'HorizontalAlignment','center')


#text(0.025,0.95,'(a)','Units','normalized','FontSize',16)
text(-0.15,1.15,'(a)','Units','normalized','FontSize',18)


CI = [lowBnd hiBnd];

#Uncomment below for 99.7# CI
# plot([lowBnd2 lowBnd2], [0 y(r==lowBnd2)],'r','LineWidth',2.5)
# plot([hiBnd2 hiBnd2], [0 y(r==hiBnd2)],'r','LineWidth',2.5)
#
# plot([lowBnd2 hiBnd2], [1.15.*max(y) 1.15.*max(y)],'r','LineWidth',2.5)
# text(k,1.1.*max(y),'99.7#','Color','r','FontSize',14,'HorizontalAlignment','center')

## Plot the unbiased ratio fig 1b
#Inferred distribution of the numbers of appointments if the selectors made multiple new selections

bigF = ra./n;
r = 0:n; #sampling
yunb = binopdf(r,n,bigF);

subplot(2,1,2)

plot(r,yunb,'k','LineWidth',2.5);
hold on
xlim([0 n]);
ylabel('P_S(R)')
xlabel('R')

handle = gca;
handle.XMinorTick = 'on';
handle.YMinorTick = 'on';
handle.TickDir = 'out';
handle.TickLength = [.02 .02];
handle.Box = 'off';
handle.Color = 'none';
handle.FontSize = 14;
handle.YGrid = 'on';

text(-0.15,1.15,'(b)','Units','normalized','FontSize',18)


## PLot 95# CI values of a resampled appointments

bnpMean = n*bigF;
bnpSTD = sqrt(n*bigF*(1-bigF));

#alp = 1-0.95/2;

# lowBnd2 = bnpMean-3*bnpSTD;
# hiBnd2 = bnpMean+3*bnpSTD;

lowBndR = bnpMean-2*bnpSTD;
hiBndR = bnpMean+2*bnpSTD;

# lowBnd2 = round(lowBnd2);
lowBndR = round(lowBndR);

# hiBnd2 = round(hiBnd2);
hiBndR = round(hiBndR);

# Catching for values over/under
# if lowBnd2 < 0
#     lowBnd2 = 0;
# end

if lowBndR < 0
    lowBndR = 0;
end

# if hiBnd2 > n
#     hiBnd2 = n;
# end

if hiBndR > n
    hiBndR = n;
end




#plot([lowBnd lowBnd], [0 y(r==lowBnd)],'b','LineWidth',2.5)
#plot([hiBnd hiBnd], [0 y(r==hiBnd)],'b','LineWidth',2.5)

plot([lowBndR hiBndR], [1.1.*max(yunb) 1.1.*max(yunb)],'r','LineWidth',2.5)

scatter(ra, 1.1.*max(yunb), 70, 'r','filled')

text(ra,1.2.*max(yunb),'95# CI','Color','r','FontSize',14,'HorizontalAlignment','center')


area(r(lowBnd+1:hiBnd+1),yunb(lowBnd+1:hiBnd+1),'FaceColor','b')


#U = trapz(r(lowBnd+1:hiBnd+1),yunb(lowBnd+1:hiBnd+1)); #Calc U using
#integration

#As defined in the appendix
U = sum(yunb(lowBnd+1:hiBnd+1));

## Add on PU text
PUround = round(U,2,'significant');

if ra < n/2

text(5*n/8,3*max(yunb)/4,['U = ' num2str(PUround)],'Color','b','FontSize',14,'HorizontalAlignment','center')

else

text(n/4,3*max(yunb)/4,['U = ' num2str(PUround)],'Color','b','FontSize',14,'HorizontalAlignment','center')


end


end

# return [CI,cdfra,B,U]