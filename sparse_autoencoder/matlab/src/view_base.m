function [] = view_base(time)


path = 'bases/';
files = dir([path 'weights1-*' num2str(time) '.dat']);
l = length(files);
for j=1:l
     file = [path, files(j).name];
     close all 
     W  = dlmread(file);
     disp(file);
     figure, display_network(W');
     pause;  
end
close all

