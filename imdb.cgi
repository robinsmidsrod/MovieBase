#!/usr/bin/perl

use strict;

use IMDB::Film;
use IMDB::Persons;
use CGI;
use Data::Dumper;

# Init CGI query object
our $q=new CGI;

# Print basic query meny unless called with parameters
unless($q->param()) {
	print $q->header;
	print $q->start_html(-title=>'MovieBase', -style=>{'src'=>'style.css'});

	print "<div class=\"search\">\n";
	print $q->start_form;
	print "Search: ";
	print $q->popup_menu('req',[ 'film','person' ],'film');
	print $q->textfield('query');
	print $q->submit('Lookup'), $q->br();
	print $q->end_form;
	print "</div>\n";
	print $q->end_html();
	exit;
}


# Print out person info from IMDB
if ($q->param('req') eq 'person') {
	my $person=new IMDB::Persons(crit => $q->param('query'));
	
	print $q->header();
	my $name=$person->name;
	print $q->start_html(-title=>'Person: ' . $name, -style=>{'src'=>'style.css'});

	print "<div class=\"search\">\n";
	print $q->start_form;
	print "Search: ";
	print $q->popup_menu('req',[ 'film','person' ],$q->param('req'));
	print $q->textfield('query',$q->param('query'));
	print $q->submit('Lookup'), $q->br();
	print $q->end_form;
	print "</div>\n";

	print "<div class=\"content\">\n";	
	print '<a target="_blank" href="http://www.imdb.com/name/nm' . $person->code . '">' . $name, "</a>\n";
	if ($person->date_of_birth) {
		print " (", $person->date_of_birth, ")<br />\n";
	} else {
		print "<br />\n";
	}

	print "<br />\n";
	
	# Referral blocking
	#print "Photo: ", "<img src=\"", $person->photo, "\" alt=\"Photo of ", $person->name, "\" />", "<br />\n";

	print "<b>Biography:</b> ", $person->mini_bio, "\n" if $person->mini_bio;
	
	print "</div>\n";
	
	my @film;
	foreach my $film (@{ $person->filmography() }) {
		(my $role, my @altnames)=split(' ... aka ',$film->{'role'});
		my $entry='<li>' . '<a href="?req=film;query=' . $film->{'code'} . '">' .
		 $film->{'title'} . '</a>';
		if (defined($film->{'year'})) {
			$entry.=' (' . $film->{'year'} . ')';
		}
		
		if (defined($role)) {
			$entry.=' (' . $role . ')';
		}		 
		
		if (scalar @altnames > 0) {
			$entry.='<br /><i>... aka ' . join("<br />\n... aka ", @altnames) . "</i>";
		}
		 
		$entry.='</li>';
		push @film, $entry;
	}
	print "<div class=\"list\">\n";
	print "<b>Filmography:</b> <br />\n<ul>", join("\n", @film), "</ul>\n";
	print "</div>\n";

	if ($person->matched) {
		print "<div class=\"match\">\n";
		my @match;
		foreach my $match (@{ $person->matched }) { push @match, '<li>' . '<a href="?req=person;query=' . $match->{'id'} . '">' . $match->{'title'} . '</a>' . '</li>'; }
		print "<b>Other matches:</b><br />\n<ul>\n", join("\n", @match), "</ul>\n";
		print "</div>\n";
	}

	print $q->end_html();
	
} elsif ($q->param('req') eq 'film') {

	my $film=new IMDB::Film(crit => $q->param('query'));

	print $q->header();
	my $title=$film->title;
	print $q->start_html(-title=>'Film: ' . $title, -style=>{'src'=>'style.css'});
	
	print "<div class=\"search\">\n";
	print $q->start_form;
	print "Search: ";
	print $q->popup_menu('req',[ 'film','person' ],$q->param('req'));
	print $q->textfield('query',$q->param('query'));
	print $q->submit('Lookup'), $q->br();
	print $q->end_form;
	print "</div>\n";
	
	print "<div class=\"content\">\n";
	print '<a target="_blank" href="http://www.imdb.com/title/tt' . $film->code . '">' . $title, "</a>\n";
	print " (", $film->year, ")<br />\n" if $film->year;

	# Referral block
	#print "Cover: ", "<img src=\"", $film->cover, "\" alt=\"Cover of ", $film->title, "\" />", "<br />\n";

	print "<i>", $film->tagline, "</i><br />\n" if $film->tagline;
	print "<br />\n";
	
	print "<b>Genre:</b> ", join(', ',@{ $film->genres }), "<br />\n<br />\n" if $film->genres;

	if ($film->full_plot) {
		print "<b>Plot:</b> ", $film->full_plot, "<br />\n<br />\n" if $film->full_plot;
	} else {
		print "<b>Plot:</b> ", $film->plot, "<br />\n<br />\n" if $film->plot;
	}

	if ($film->rating) {
		(my $rating,my $voters)=$film->rating;
		my $vote=$voters ? ' (' . $voters . ' votes)' : '';
		print "<b>Rating:</b> ", $rating, $vote, "<br />\n<br />\n";
	}

	my @directors;
	foreach my $director (@{ $film->directors() }) {
		push @directors,
		 '<a href="?req=person;query=' . $director->{'id'} . '">' .
		 $director->{'name'} .
		 '</a>';
	}
	print "<b>Directors:</b> ", join(', ', @directors), "<br />\n";

	my @writers;
	foreach my $writer (@{ $film->writers() }) {
		push @writers,
		 '<a href="?req=person;query=' . $writer->{'id'} . '">' .
		 $writer->{'name'} .
		 '</a>';
	}
	print "<b>Writers:</b> ", join(', ',@writers), "<br />\n<br />\n";

	print "<b>Duration:</b> ", $film->duration, "<br />\n" if $film->duration;
	print "<b>Country:</b> ", join(', ',@{ $film->country }), "<br />\n";
	print "<b>Language:</b> ", join(', ',@{ $film->language }), "<br />\n";

	my @cert;
	my %cert=%{ $film->certifications };
	foreach my $cert (sort keys %cert) { push @cert, $cert . ' (' . $cert{$cert} . ')'; }
	print "<b>Certifications:</b> ", join(', ', @cert), "<br />\n";
	print "</div>\n";

	print "<div class=\"list\">\n";
	my @cast;
	foreach my $cast (@{ $film->cast() }) {
		my $role=$cast->{'role'} ? ' (' . $cast->{'role'} . ')' : '';
		my $entry='<li>' . '<a href="?req=person;query=' . $cast->{'id'} . '">' . $cast->{'name'} . '</a>' . $role . "</li>";
		push @cast, $entry;
	}
	print "<b>Cast:</b><br />\n<ul>\n", join("\n",@cast), "</ul>\n";
	print "</div>\n";

	if ($film->matched) {
		print "<div class=\"match\">\n";
		my @match;
		foreach my $match (@{ $film->matched }) { push @match, '<li>' . '<a href="?req=film;query=' . $match->{'id'} . '">' . $match->{'title'} . '</a>' . '</li>'; }
		print "<b>Other matches:</b><br />\n<ul>\n", join("\n", @match), "</ul>\n";
		print "</div>\n";
	}
	
	print $q->end_html();

}