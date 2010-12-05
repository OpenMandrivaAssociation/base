# (oe) undefining these makes the build _real_ quick.
%undefine __find_provides
%undefine __find_requires

Summary:	Basic Analysis and Security Engine
Name:		base
Version:	1.4.4
Release:	%mkrel 2
License:	GPLv2+
Group:		System/Servers
URL:		http://base.secureideas.net/
Source0:	http://prdownloads.sourceforge.net/secureideas/%{name}-%{version}.tar.gz
Patch0:		base-1.2.4-mdv_conf.diff
Requires(pre):	apache-mod_php apache-mod_ssl php-mysql php-sockets php-adodb
Requires:	apache-mod_php apache-mod_ssl php-mysql php-sockets php-adodb
Requires(post):	ccp >= 0.4.0
Requires(post):	rpm-helper
Requires:	php-pear-Image_Graph
Requires:	php-pear-Numbers_Words
Requires:	php-pear-Image_Graph
BuildArch:	noarch
BuildRequires:	dos2unix
BuildRequires:	apache-base >= 2.0.54
Provides:	acid
Obsoletes:	acid
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
BASE is the Basic Analysis and Security Engine. It is based on the code from
the Analysis Console for Intrusion Databases (ACID) project. This application
provides a web front-end to query and analyze the alerts coming from a SNORT
IDS system. BASE is a web interface to perform analysis of intrusions that
snort has detected on your network. It uses a user authentication and role-base
system, so that you as the security 'admin can decide what and how much
information each user can see.  It also has a simple to use, web-based setup
program for people not comfortable with editing files directly.

%prep

%setup -q
%patch0 -p0

rm -rf docs/contrib

# clean up CVS stuff
for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -r $i; fi >&/dev/null
done

# fix dir perms
find . -type d | xargs chmod 755

# fix file perms
find . -type f | xargs chmod 644

# strip away annoying ^M
find -type f | grep -v "\.gif" | grep -v "\.png" | grep -v "\.jpg" | xargs dos2unix -U

# instead of a patch
find -type f | xargs perl -pi -e "s|base_conf\.php|/etc/base/base_conf.php|g"
find -type f | xargs perl -pi -e "s|\.\.\/\/etc\/base\/base_conf\.php|/etc/base/base_conf.php|g"

%build

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d
install -d %{buildroot}%{_sysconfdir}/%{name}
install -d %{buildroot}/var/www/%{name}

cp -aRf * %{buildroot}/var/www/%{name}/

install -m0644 base_conf.php.dist %{buildroot}%{_sysconfdir}/%{name}/base_conf.php

cat > README.MDK << EOF
S E T U P  H O W T O
--------------------

There is two ways to configure %{name}-%{version}

1. As root edit the %{_sysconfdir}/%{name}/base_conf.php file (easier)

2. rm -f %{_sysconfdir}/%{name}/base_conf.php
   touch %{_sysconfdir}/%{name}/base_conf.php
   chown apache:apache /var/www/%{name}
   chown apache:apache %{_sysconfdir}/%{name}/base_conf.php
   chmod 666 %{_sysconfdir}/%{name}/base_conf.php
   go to http://localhost/base/
EOF

cat > %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf << EOF

Alias /%{name} /var/www/%{name}

<Directory /var/www/%{name}>
    Allow from All
</Directory>

#<LocationMatch /%{name}>
#    Options FollowSymLinks
#    RewriteEngine on
#    RewriteCond %{SERVER_PORT} !^443$
#    RewriteRule ^.*$ https://%{SERVER_NAME}%{REQUEST_URI} [L,R]
#</LocationMatch>

EOF

# cleanup
rm -rf %{buildroot}/var/www/%{name}/docs
rm -f %{buildroot}/var/www/%{name}/base_conf.php.dist
rm -f %{buildroot}/var/www/%{name}/README.MDK

%post
ccp --delete --ifexists --set "NoOrphans" --ignoreopt config_version --oldfile %{_sysconfdir}/%{name}/base_conf.php --newfile %{_sysconfdir}/%{name}/base_conf.php.rpmnew
%_post_webapp

%postun
%_postun_webapp

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc docs/* README.MDK
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf
%dir %attr(0755,root,root) %{_sysconfdir}/%{name}
%attr(0640,apache,root) %config(noreplace) %{_sysconfdir}/%{name}/base_conf.php
/var/www/%{name}
