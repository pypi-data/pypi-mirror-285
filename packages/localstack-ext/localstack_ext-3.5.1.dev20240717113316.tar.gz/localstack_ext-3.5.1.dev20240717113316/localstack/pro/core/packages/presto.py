import os
from typing import List
from localstack.constants import MAVEN_REPO_URL
from localstack.packages import InstallTarget,Package
from localstack.packages.core import ArchiveDownloadAndExtractInstaller
from localstack.pro.core.packages.bigdata_common import bigdata_jar_cache_dir,download_and_cache_jar_file
from localstack.pro.core.packages.cve_fixes import CVEFix,FixStrategyDelete,fix_cves_in_jar_files
from localstack.utils.files import cp_r,save_file
URL_PATTERN_PRESTO=f"{MAVEN_REPO_URL}/io/trino/trino-server/<version>/trino-server-<version>.tar.gz"
PRESTO_DEFAULT_VERSION='389'
PRESTO_VERSIONS=[PRESTO_DEFAULT_VERSION]
PRESTO_JVM_CONFIG='\n-server\n-Xmx1G\n-XX:-UseBiasedLocking\n-XX:+UseG1GC\n-XX:+UseGCOverheadLimit\n-XX:+ExplicitGCInvokesConcurrent\n-XX:+HeapDumpOnOutOfMemoryError\n-XX:+ExitOnOutOfMemoryError\n-XX:ReservedCodeCacheSize=150M\n-Duser.timezone=UTC\n-Djdk.attach.allowAttachSelf=true\n-Djdk.nio.maxCachedBufferSize=2000000\n-Dpresto-temporarily-allow-java8=true\n'
PRESTO_CONFIG_PROPS='\nnode.id=presto-master\nnode.environment=test\ncoordinator=true\nnode-scheduler.include-coordinator=true\nhttp-server.http.port=8080\nquery.max-memory=512MB\nquery.max-memory-per-node=512MB\n# query.max-total-memory-per-node=512MB\ndiscovery-server.enabled=true\ndiscovery.uri=http://localhost:8080\nprotocol.v1.alternate-header-name=Presto\n'
class PrestoInstaller(ArchiveDownloadAndExtractInstaller):
	def __init__(A,version):super().__init__(name='presto',version=version,extract_single_directory=True)
	def _get_install_marker_path(A,install_dir):return os.path.join(install_dir,'bin','launcher')
	def _get_download_url(A):return URL_PATTERN_PRESTO.replace('<version>',A.version)
	def _post_process(C,target):
		H='config.properties';G='jvm.config';B=target;from localstack.pro.core.packages.hive import ICEBERG_JAR_URL as I;from localstack.pro.core.packages.spark import spark_common_driver_package as D;E=C.get_installed_dir();A=os.path.join(E,'etc')
		if not os.path.exists(os.path.join(A,G)):save_file(os.path.join(A,G),PRESTO_JVM_CONFIG)
		if not os.path.exists(os.path.join(A,H)):save_file(os.path.join(A,H),PRESTO_CONFIG_PROPS)
		J=os.path.join(E,'lib');D.install(target=B);K=D.get_installed_dir();L=bigdata_jar_cache_dir(target=B);M=download_and_cache_jar_file(jar_url=I,cache_dir=L,target_dir=K);F=os.path.join(J,'iceberg.jar')
		if not os.path.exists(F):cp_r(M,F)
		C._apply_cve_fixes(B)
	def _apply_cve_fixes(B,target):A=CVEFix(paths=['presto/389/plugin/phoenix5/trino-phoenix5-patched-389.jar','presto/389/plugin/pinot/helix-core-0.9.8.jar','presto/389/plugin/accumulo/log4j-1.2.17.jar'],strategy=FixStrategyDelete());fix_cves_in_jar_files(target,fixes=[A])
class PrestoPackage(Package):
	def __init__(A,default_version=PRESTO_DEFAULT_VERSION):super().__init__(name='Presto',default_version=default_version)
	def get_versions(A):return PRESTO_VERSIONS
	def _get_installer(A,version):return PrestoInstaller(version)
presto_package=PrestoPackage()