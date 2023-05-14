mat = dlmread('./output.txt');
% Change this for different plots; max is length(mat(1, 2:end)), can change to any value less than that
count = 1;
figure;
function rv = plt(mat, maxVal)
  % Splits matrix into multiprocessed, singleprocessed, and number of cells.
  mTimes = mat(1, 2:maxVal);
  sTimes = mat(2, 2:maxVal);
  totalCells = mat(3, 2:maxVal);

  # Create line of best fit for both multiprocessed and singleprocessed.
  mcoeff = polyfit(mTimes, totalCells, 1);
  scoeff = polyfit(sTimes, totalCells, 1);
  mx = linspace(0, max(mTimes));
  sx = linspace(0, max(sTimes));
  my = polyval(mcoeff, mx);
  sy = polyval(scoeff, sx);
  % Plot lines of best fit along with data points.
  hold on
  scatter(totalCells, mTimes, '.b')
  scatter(totalCells, sTimes, '.r')
  plot(my, mx, '-b', sy, sx, '-r')

  ylabel('Average execution time (ms)')
  xlabel('Cell number')
  xlim([0 inf])
  ylim([0 inf])

  hold off
end

if length(mat(1, 2:end)) < 50
  maxVal=length(mat(1, 2:end))
  plt(mat, maxVal)

else
  for maxVal=[10 20 50 length(mat(1, 2:end))]
    subplot(2, 2, count)
    plt(mat, maxVal)
    title([num2str(maxVal) ' Values from dataset'])
    count++;
    set(gca, 'fontsize', 6)
  endfor
end

S = axes('visible', 'off', 'title', "Multithreaded (blue) vs. Singlethreaded (red) execution of Conway's Game of Life", "FontSize", 9);
print -dpng graph.png