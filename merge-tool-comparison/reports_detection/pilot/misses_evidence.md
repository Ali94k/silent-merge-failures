==========================================================================================
MERGE apache_shiro__13806fc623
  labels: mergiraf=Tests_failed git=Tests_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=25.0
  FILE web/src/test/java/org/apache/shiro/web/mgt/CookieRememberMeManagerTest.java  (merge_outcome=clean)
    base->ours 22 chg-lines | base->theirs 2 | merged==dev(ws-norm): True
==========================================================================================
MERGE blockchain_api-v1-client-java__abdf54e6ab
  labels: mergiraf=Tests_failed git=Merge_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=12.0
  FILE src/main/java/info/blockchain/api/HttpClient.java  (merge_outcome=clean)
    base->ours 23 chg-lines | base->theirs 8 | merged==dev(ws-norm): False
    merged-vs-dev diff (9 lines):
      @@ -63,6 +63,7 @@
               if (requestMethod.equals("GET")) {
      -            if (encodedParams.isEmpty()) {
      +            if(encodedParams.isEmpty()) {
                       url = new URL(BASE_URL + resource);
      -            } else {
      -                url = new URL(BASE_URL + resource + '?' + encodedParams);
      +            }
      +            else {
      +                url = new URL(baseURL + resource + '?' + encodedParams);
                   }
==========================================================================================
MERGE camsys_onebusaway-application-modules__915e2f3ffe
  labels: mergiraf=Tests_failed git=Tests_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=71.0
  FILE onebusaway-transit-data-federation/src/main/java/org/onebusaway/transit_data_federation/impl/beans/StopWithArrivalsAndDeparturesBeanServiceImpl.java  (merge_outcome=clean)
    base->ours 2 chg-lines | base->theirs 12 | merged==dev(ws-norm): True
==========================================================================================
MERGE cloudfoundry_cf-java-client__80d0a0dff9
  labels: mergiraf=Tests_failed git=Tests_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=108.0
  FILE cloudfoundry-operations/src/main/java/org/cloudfoundry/operations/serviceadmin/DefaultServiceAdmin.java  (merge_outcome=clean)
    base->ours 79 chg-lines | base->theirs 23 | merged==dev(ws-norm): False
    merged-vs-dev diff (6 lines):
      @@ -142,3 +142,3 @@
               return this.cloudFoundryClient
      -            .flatMap(cloudFoundryClient -> Mono.zip(
      +            .then(cloudFoundryClient -> Mono.when(
                       Mono.just(cloudFoundryClient),
      @@ -146,3 +146,3 @@
                   ))
      -            .flatMap( function((cloudFoundryClient, serviceBrokerId) -> requestUpdateServiceBroker(cloudFoundryClient, request, serviceBrokerId)))
      +            .then(function((cloudFoundryClient, serviceBrokerId) -> requestUpdateServiceBroker(cloudFoundryClient, request, serviceBrokerId)))
                   .then()
==========================================================================================
MERGE cloudfoundry_cf-java-client__9f6b79e294
  labels: mergiraf=Tests_failed git=Tests_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=117.0
  FILE cloudfoundry-operations/src/main/java/org/cloudfoundry/operations/applications/DefaultApplications.java  (merge_outcome=clean)
    base->ours 192 chg-lines | base->theirs 125 | merged==dev(ws-norm): False
    merged-vs-dev diff (20 lines):
      @@ -294,4 +294,4 @@
               return Mono
      -            .zip(this.cloudFoundryClient, this.spaceId)
      -            .flatMap(function((cloudFoundryClient, spaceId) -> Mono.zip(
      +            .when(this.cloudFoundryClient, this.spaceId)
      +            .then(function((cloudFoundryClient, spaceId) -> Mono.when(
                       Mono.just(cloudFoundryClient),
      @@ -436,4 +436,4 @@
               return Mono
      -            .zip(this.cloudFoundryClient, this.spaceId)
      -            .flatMap(function((cloudFoundryClient, spaceId) -> Mono.zip(
      +            .when(this.cloudFoundryClient, this.spaceId)
      +            .then(function((cloudFoundryClient, spaceId) -> Mono.when(
                       Mono.just(cloudFoundryClient),
      @@ -441,3 +441,3 @@
                   ))
      -            .flatMap(function((cloudFoundryClient, applicationId) -> requestCreateTask(cloudFoundryClient, applicationId, request)))
      +            .then(function((cloudFoundryClient, applicationId) -> requestCreateTask(cloudFoundryClient, applicationId, request)))
                   .map(DefaultApplications::toTask)
      @@ -530,4 +530,4 @@
               return Mono
      -            .zip(this.cloudFoundryClient, this.spaceId)
      -            .flatMap(function((cloudFoundryClient, spaceId) -> Mono.zip(
      +            .when(this.cloudFoundryClient, this.spaceId)
      +            .then(function((cloudFoundryClient, spaceId) -> Mono.when(
                       Mono.just(cloudFoundryClient),
      @@ -535,3 +535,3 @@
                   ))
      -            .flatMap(function((cloudFoundryClient, applicationId) -> Mono.zip(
      +            .then(function((cloudFoundryClient, applicationId) -> Mono.when(
                       Mono.just(cloudFoundryClient),
      @@ -539,3 +539,3 @@
                   ))
      -            .flatMap(function(DefaultApplications::requestTerminateTask))
      +            .then(function(DefaultApplications::requestTerminateTask))
                   .then()
==========================================================================================
MERGE cternes_openkeepass__bb53512ab2
  labels: mergiraf=Tests_failed git=Merge_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=3 materialized=2 diverged=0 num_diff_files=94.0
  FILE src/test/java/de/slackspace/openkeepass/reader/KeepassDatabaseReaderTest.java  (merge_outcome=clean)
    base->ours 25 chg-lines | base->theirs 69 | merged==dev(ws-norm): False
    merged-vs-dev diff (22 lines):
      @@ -14,2 +14,3 @@
       import de.slackspace.openkeepass.domain.CrsAlgorithm;
      +import de.slackspace.openkeepass.domain.CustomIcons;
       import de.slackspace.openkeepass.domain.Entry;
      @@ -190,2 +191,21 @@
       	}
      +	@Test
      +	public void whenUsingCustomIconsShouldReturnImageData() throws IOException {
      +		KeePassFile database = KeePassDatabase.getInstance("target/test-classes/IconsDatabase.kdbx").openDatabase("abcdefg");
      +		CustomIcons customIcons = database.getMeta().getCustomIcons();
      +		Assert.assertEquals(1, customIcons.getIcons().size());
      +		List<Group> groups = database.getGroups();
      +		Assert.assertEquals(1, groups.size());
      +		Group group = database.getGroupByName("SomeGroup");
      +		Assert.assertNotNull(group);
      +		Entry entry = database.getEntryByTitle("SomeEntry");
      +		Assert.assertNotNull(entry);
      +		byte[] groupData = group.getIconData();
      +		Assert.assertNotNull(groupData);
      +		byte[] entryData = entry.getIconData();
      +		Assert.assertNotNull(entryData);
      +		Assert.assertArrayEquals("group and entry icon are different", groupData, entryData);
      +		// Note: can't seem to get a comparison with a static test.png file to work
      +		// original file is different in size and even the exported custom icon via KeePass GUI has different bytes
      +	}
       }
  FILE src/main/java/de/slackspace/openkeepass/KeePassDatabase.java  (merge_outcome=clean)
    base->ours 25 chg-lines | base->theirs 57 | merged==dev(ws-norm): True
==========================================================================================
MERGE erudika_para__a9e67cc8b3
  labels: mergiraf=Tests_failed git=Merge_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=11.0
  FILE para-server/src/main/java/com/erudika/para/aop/IndexAndCacheAspect.java  (merge_outcome=clean)
    base->ours 125 chg-lines | base->theirs 21 | merged==dev(ws-norm): False
    merged-vs-dev diff (14 lines):
      @@ -90,3 +90,3 @@
       	public Object invoke(MethodInvocation mi) throws Throwable {
      -		Method m = mi.getMethod();
      +		Method method = mi.getMethod();
       		Object[] args = mi.getArguments();
      @@ -98,3 +98,3 @@
       			detectNestedInvocations(m);
      -			superMethod = DAO.class.getMethod(m.getName(), m.getParameterTypes());
      +			superMethod = DAO.class.getMethod(method.getName(), method.getParameterTypes());
       			indexedAnno = Config.isSearchEnabled() ? superMethod.getAnnotation(Indexed.class) : null;
      @@ -105,3 +105,3 @@
       		if (!Modifier.isPublic(mi.getMethod().getModifiers())) {
      -			return invokeDAO(appid, m, mi);
      +			return invokeDAO(appid, method, mi);
       		}
      @@ -112,4 +112,4 @@
       		}
      -		Object result = handleIndexing(indexedAnno, appid, m, args, mi);
      -		Object cachingResult = handleCaching(cachedAnno, appid, m, args, mi);
      +		Object result = handleIndexing(indexedAnno, appid, method, args, mi);
      +		Object cachingResult = handleCaching(cachedAnno, appid, method, args, mi);
       		// we have a read operation without any result but we get back objects from cache
      @@ -120,3 +120,3 @@
       		if (indexedAnno == null && cachedAnno == null) {
      -			result = invokeDAO(appid, m, mi);
      +			result = invokeDAO(appid, method, mi);
       		}
==========================================================================================
MERGE jacquesberger_jsonparsingexample__ac521954c2
  labels: mergiraf=Tests_failed git=Merge_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=2.0
  FILE src/main/java/org/jberger/jsonparsingexample/json/JSON.java  (merge_outcome=clean)
    base->ours 8 chg-lines | base->theirs 8 | merged==dev(ws-norm): False
    merged-vs-dev diff (6 lines):
      @@ -28,3 +28,3 @@
           private static void saveToFiles(ArrayList<String> bookTitles) throws IOException {
      -        JSONArray bookTitleList = initializeBookList(bookTitles);
      +        JSONArray outputList = initializeBookList(bookTitles);
               saveAsRawJsonFile(bookTitleList);
      @@ -37,3 +37,3 @@
               }
      -        return bookTitleList;
      +        return outputList;
           }
==========================================================================================
MERGE javaparser_javaparser__a23c6aa3b8
  labels: mergiraf=Tests_failed git=Merge_failed spork=Tests_passed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=3 materialized=1 diverged=0 num_diff_files=33.0
  FILE javaparser-testing/src/test/java/com/github/javaparser/bdd/steps/DumpingSteps.java  (merge_outcome=clean)
    base->ours 14 chg-lines | base->theirs 43 | merged==dev(ws-norm): False
    merged-vs-dev diff (9 lines):
      @@ -25,3 +25,2 @@
       import com.github.javaparser.ast.Node;
      -import com.github.javaparser.ast.visitor.DumpVisitor;
       import org.jbehave.core.annotations.Given;
      @@ -35,3 +34,3 @@
       import java.net.URL;
      -import static org.hamcrest.CoreMatchers.is;
      +import static org.hamcrest.CoreMatchers.*;
       import static org.junit.Assert.assertEquals;
      @@ -45,3 +44,3 @@
           }
      -    @Given("the {class|compilation unit|expression|block|expressions|statement|import|annotation|body declaration} in the file \"$classFile\"")
      +    @Given("the class in the file \"$classFile\"")
           public void givenTheClassInTheFile(String classFile) throws URISyntaxException, IOException, ParseException {
      @@ -80,3 +79,3 @@
           public void isDumpedTo(String dumpSrc) {
      -        assertEquals(dumpSrc.trim(), resultNode.toString().trim());
      +         assertEquals(dumpSrc.trim(), resultNode.toString().trim());
           }
==========================================================================================
MERGE jnr_jnr-unixsocket__467698b6bd
  labels: mergiraf=Tests_failed git=Merge_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=3 materialized=2 diverged=0 num_diff_files=8.0
  FILE src/main/java/jnr/unixsocket/UnixSocketChannel.java  (merge_outcome=clean)
    base->ours 15 chg-lines | base->theirs 17 | merged==dev(ws-norm): True
  FILE src/main/java/jnr/unixsocket/Native.java  (merge_outcome=clean)
    base->ours 50 chg-lines | base->theirs 6 | merged==dev(ws-norm): False
    merged-vs-dev diff (10 lines):
      @@ -28,5 +28,3 @@
       import jnr.ffi.Platform;
      -import jnr.ffi.Pointer;
       import jnr.ffi.Runtime;
      -import jnr.ffi.Struct;
       import jnr.ffi.annotations.In;
      @@ -137,2 +135,5 @@
           }
      +    public static boolean getboolsockopt (int s, SocketLevel level, int optname) {
      +        return getsockopt(s, level, optname) != 0;
      +    }
           public static int getsockopt(int s, SocketLevel level, SocketOption optname, Struct data) {
      @@ -143,5 +144,2 @@
           }
      -    public static boolean getboolsockopt (int s, SocketLevel level, int optname) {
      -        return getsockopt(s, level, optname) != 0;
      -    }
       }
==========================================================================================
MERGE kaazing_robot__084cc0b426
  labels: mergiraf=Tests_failed git=Merge_failed spork=Merge_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=144.0
  FILE specification/wse/src/test/java/org/kaazing/specification/wse/data/BinaryAsEscapedTextIT.java  (merge_outcome=clean)
    base->ours 8 chg-lines | base->theirs 10 | merged==dev(ws-norm): False
    merged-vs-dev diff (4 lines):
      @@ -37,2 +37,3 @@
           }
      +    @Test
           @Specification({"echo.non.escaped.characters/request",
      @@ -51,2 +52,3 @@
           @Ignore("To be completed when wse spec is complete")
      +    @Ignore("Escaping is underspecified, see https://github.com/k3po/k3po/pull/280/files")
           @Specification({
==========================================================================================
MERGE mikera_vectorz__d93ef1b341
  labels: mergiraf=Tests_failed git=Tests_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=20.0
  FILE src/test/java/mikera/matrixx/TestMatrices.java  (merge_outcome=clean)
    base->ours 4 chg-lines | base->theirs 1 | merged==dev(ws-norm): True
==========================================================================================
MERGE mitre_http-proxy-servlet__b7a68118f2
  labels: mergiraf=Tests_failed git=Tests_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=6.0
  FILE src/main/java/org/mitre/dsmiley/httpproxy/ProxyServlet.java  (merge_outcome=clean)
    base->ours 133 chg-lines | base->theirs 3 | merged==dev(ws-norm): True
==========================================================================================
MERGE named-data_jndn__3d47402192
  labels: mergiraf=Tests_failed git=Tests_failed spork=Tests_passed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=7.0
  FILE src/net/named_data/jndn/NetworkNack.java  (merge_outcome=clean)
    base->ours 4 chg-lines | base->theirs 10 | merged==dev(ws-norm): True
==========================================================================================
MERGE nysenate_openlegislation__9c7cf034c1
  labels: mergiraf=Tests_failed git=Merge_failed spork=Merge_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=3 materialized=1 diverged=0 num_diff_files=646.0
  FILE src/main/java/gov/nysenate/openleg/search/committee/ElasticCommitteeSearchDao.java  (merge_outcome=clean)
    base->ours 21 chg-lines | base->theirs 17 | merged==dev(ws-norm): False
    merged-vs-dev diff (23 lines):
      @@ -3,10 +3,10 @@
       import gov.nysenate.openleg.api.legislation.committee.view.CommitteeView;
      +import gov.nysenate.openleg.common.dao.LimitOffset;
      +import gov.nysenate.openleg.legislation.SessionYear;
      +import gov.nysenate.openleg.legislation.committee.*;
      +import gov.nysenate.openleg.legislation.committee.dao.CommitteeDataService;
       import gov.nysenate.openleg.search.ElasticBaseDao;
      -import gov.nysenate.openleg.common.dao.LimitOffset;
       import gov.nysenate.openleg.search.SearchIndex;
      -import gov.nysenate.openleg.legislation.committee.*;
      -import gov.nysenate.openleg.legislation.SessionYear;
       import gov.nysenate.openleg.search.SearchResult;
       import gov.nysenate.openleg.search.SearchResults;
      -import gov.nysenate.openleg.legislation.committee.dao.CommitteeDataService;
       import org.elasticsearch.action.bulk.BulkRequest;
      @@ -19,4 +19,2 @@
       import org.elasticsearch.search.sort.SortBuilder;
      -import org.slf4j.Logger;
      -import org.slf4j.LoggerFactory;
       import org.springframework.beans.factory.annotation.Autowired;
      @@ -34,5 +32,8 @@
       public class ElasticCommitteeSearchDao extends ElasticBaseDao implements CommitteeSearchDao {
      -    private static final Logger logger = LoggerFactory.getLogger(ElasticCommitteeSearchDao.class);
           private static final String committeeSearchIndexName = SearchIndex.COMMITTEE.getIndexName();
      -    @Autowired private CommitteeDataService committeeDataService;
      +    private final CommitteeDataService committeeDataService;
      +    @Autowired
      +    public ElasticCommitteeSearchDao(CommitteeDataService committeeDataService) {
      +        this.committeeDataService = committeeDataService;
      +    }
           @Override
      @@ -81,4 +82,4 @@
                       getCommitteeSessionQuery(committeeSessionId), null, Collections.emptyList(), LimitOffset.ALL);
      -        searchResults.getResults().stream()
      -                .map(SearchResult::getResult)
      +        searchResults.resultList().stream()
      +                .map(SearchResult::result)
                       .map(this::getCommitteeVersionDeleteRequest)
==========================================================================================
MERGE openhft_chronicle-bytes__5bad7e86ea
  labels: mergiraf=Tests_failed git=Tests_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=25.0
  FILE src/main/java/net/openhft/chronicle/bytes/NativeBytes.java  (merge_outcome=clean)
    base->ours 24 chg-lines | base->theirs 3 | merged==dev(ws-norm): True
==========================================================================================
MERGE openhft_chronicle-bytes__e3ac571d25
  labels: mergiraf=Tests_failed git=Merge_failed spork=Tests_passed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=6.0
  FILE src/test/java/net/openhft/chronicle/bytes/BytesTest.java  (merge_outcome=clean)
    base->ours 13 chg-lines | base->theirs 34 | merged==dev(ws-norm): False
    merged-vs-dev diff (26 lines):
      @@ -802,2 +802,14 @@
           }
      +    @Ignore("https://github.com/OpenHFT/Chronicle-Bytes/issues/185")
      +    @Test
      +    public void capacityVsWriteLimitInvariant() {
      +        final Bytes<?> bytes = alloc1.elasticBytes(20);
      +        assertEquals(bytes.capacity(), bytes.writeLimit());
      +    }
      +    @Ignore("https://github.com/OpenHFT/Chronicle-Bytes/issues/185")
      +    @Test
      +    public void isClear() {
      +        final Bytes<?> bytes = alloc1.elasticBytes(20);
      +        assertTrue(bytes.isClear());
      +    }
           @Test
      @@ -836,14 +848,2 @@
           }
      -    @Ignore("https://github.com/OpenHFT/Chronicle-Bytes/issues/185")
      -    @Test
      -    public void capacityVsWriteLimitInvariant() {
      -        final Bytes<?> bytes = alloc1.elasticBytes(20);
      -        assertEquals(bytes.capacity(), bytes.writeLimit());
      -    }
      -    @Ignore("https://github.com/OpenHFT/Chronicle-Bytes/issues/185")
      -    @Test
      -    public void isClear() {
      -        final Bytes<?> bytes = alloc1.elasticBytes(20);
      -        assertTrue(bytes.isClear());
      -    }
       }
==========================================================================================
MERGE prism_prism-bukkit__6dfb9ef0cf
  labels: mergiraf=Tests_failed git=Tests_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=6.0
  FILE src/main/java/me/botsko/prism/commands/NearCommand.java  (merge_outcome=clean)
    base->ours 2 chg-lines | base->theirs 4 | merged==dev(ws-norm): True
==========================================================================================
MERGE prism_prism-bukkit__74927cacad
  labels: mergiraf=Tests_failed git=Merge_failed spork=Merge_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=3 materialized=2 diverged=1 num_diff_files=2.0
  FILE src/main/java/me/botsko/prism/database/DeleteQuery.java  (merge_outcome=clean)
    base->ours 1 chg-lines | base->theirs 1 | merged==dev(ws-norm): True
  FILE src/main/java/me/botsko/prism/actionlibs/ActionsQuery.java  (merge_outcome=conflict)
==========================================================================================
MERGE tabulapdf_tabula-java__767699f3aa
  labels: mergiraf=Tests_failed git=Merge_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=3 materialized=2 diverged=1 num_diff_files=6.0
  FILE src/test/java/technology/tabula/TestRegexSearch.java  (merge_outcome=clean)
    base->ours 33 chg-lines | base->theirs 741 | merged==dev(ws-norm): False
    merged-vs-dev diff (5 lines):
      @@ -7,3 +7,2 @@
       import java.util.Locale;
      -import org.apache.pdfbox.pdmodel.*;
       import org.apache.pdfbox.pdmodel.*;
      @@ -75,3 +74,3 @@
       			}
      -			RegexSearch regexSearch = new RegexSearch("Knowledge","false","Social.","false",PDDocument.load(multiPageTable),null);
      +			RegexSearch regexSearch = new RegexSearch("Knowledge","false","Social.","false",PDDocument.load(multiPageTable));
       			//TODO: The current multi-page regex capabilities WILL NOT FILTER OUT THE FOOTER--this needs to be corrected!! This test simply verifies the current program behavior
  FILE src/main/java/technology/tabula/detectors/RegexSearch.java  (merge_outcome=conflict)
==========================================================================================
MERGE thenewcircle_spring-hibernate-20120924__7ec9c1b4bb
  labels: mergiraf=Tests_failed git=Merge_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=21.0
  FILE src/main/java/com/marakana/contacts/controllers/ContactController.java  (merge_outcome=clean)
    base->ours 112 chg-lines | base->theirs 74 | merged==dev(ws-norm): False
    merged-vs-dev diff (48 lines):
      @@ -6,2 +6,3 @@
       import org.springframework.web.bind.annotation.RequestMethod;
      +import org.springframework.web.bind.annotation.RequestParam;
       import com.marakana.contacts.repositories.ContactRepository;
      @@ -16,2 +17,47 @@
       	}
      +	@RequestMapping(value = "/contact", params = "add", method = RequestMethod.GET)
      +	public String getAddContact() {
      +		return "contact/add";
      +	}
      +	@RequestMapping(value = "/contact", params = "edit", method = RequestMethod.GET)
      +	public String getEditContact(@RequestParam long id, Model model) {
      +		Contact contact = contactRepository.findOne(id);
      +		model.addAttribute("contact", contact);
      +		return "contact/edit";
      +	}
      +	@RequestMapping(value = "/contact", method = RequestMethod.GET)
      +	public String getViewContact(@RequestParam long id, Model model) {
      +		Contact contact = contactRepository.findOne(id);
      +		model.addAttribute("contact", contact);
      +		return "contact/view";
      +	}
      +	@RequestMapping(value = "/contact", params = "add", method = RequestMethod.POST)
      +	public String postAddContact(@RequestParam String name,
      +			@RequestParam String street, @RequestParam String city,
      +			@RequestParam String state, @RequestParam String zip) {
      +		Address address = new Address(street, city, state, zip);
      +		Contact contact = new Contact(name, address);
      +		contact = contactRepository.save(contact);
      +		return "redirect:contact?id=" + contact.getId();
      +	}
      +	@RequestMapping(value = "/contact", params = "edit", method = RequestMethod.POST)
      +	public String postEditContact(@RequestParam long id,
      +			@RequestParam String name, @RequestParam String street,
      +			@RequestParam String city, @RequestParam String state,
      +			@RequestParam String zip) {
      +		Contact contact = contactRepository.findOne(id);
      +		Address address = contact.getAddress();
      +		contact.setName(name);
      +		address.setStreet(street);
      +		address.setCity(city);
      +		address.setState(state);
      +		address.setZip(zip);
      +		contactRepository.save(contact);
      +		return "redirect:contact?id=" + contact.getId();
      +	}
      +	@RequestMapping(value = "/contact", params = "delete", method = RequestMethod.POST)
      +	public String postDeleteContact(@RequestParam long id) {
      +		contactRepository.delete(id);
      +		return "redirect:contacts";
      +	}
       }
==========================================================================================
MERGE winder_universal-g-code-sender__84d687330a
  labels: mergiraf=Tests_failed git=Merge_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=3 materialized=2 diverged=0 num_diff_files=110.0
  FILE ugs-core/src/com/willwinder/universalgcodesender/utils/ControllerSettings.java  (merge_outcome=clean)
    base->ours 4 chg-lines | base->theirs 161 | merged==dev(ws-norm): False
    merged-vs-dev diff (56 lines):
      @@ -18,2 +18,5 @@
       import com.willwinder.universalgcodesender.firmware.fluidnc.FluidNCController;
      +import com.willwinder.universalgcodesender.gcode.util.CommandProcessorLoader;
      +import java.util.ArrayList;
      +import java.util.List;
       import com.willwinder.universalgcodesender.G2CoreController;
      @@ -27,5 +30,2 @@
       import com.willwinder.universalgcodesender.gcode.processors.CommandProcessor;
      -import com.willwinder.universalgcodesender.gcode.util.CommandProcessorLoader;
      -import java.util.ArrayList;
      -import java.util.List;
       import java.util.Optional;
      @@ -41,25 +41,2 @@
           ProcessorConfigGroups GcodeProcessors;
      -    public enum CONTROLLER {
      -        GRBL("GRBL"),
      -        GRBL_ESP32("GRBL ESP32"),
      -        FLUIDNC("FluidNC"),
      -        SMOOTHIE("SmoothieBoard"),
      -        TINYG("TinyG"),
      -        G2CORE("g2core"),
      -        XLCD("XLCD"),
      -        LOOPBACK("Loopback"),
      -        LOOPBACK_SLOW("Loopback_Slow");
      -        final String name;
      -        CONTROLLER(String name) {
      -            this.name = name;
      -        }
      -        public static CONTROLLER fromString(String name) {
      -            for (CONTROLLER c : values()) {
      -                if (c.name.equalsIgnoreCase(name)) {
      -                    return c;
      -                }
      -            }
      -            return null;
      -        }
      -    }
           public String getName() {
      @@ -102,3 +79,3 @@
                   case FLUIDNC:
      -                return Optional.of(new FluidNCController());
      +                return new FluidNCController();
                   default:
      @@ -124,2 +101,25 @@
               return this.GcodeProcessors;
      +    }
      +    public enum CONTROLLER {
      +        GRBL("GRBL"),
      +        GRBL_ESP32("GRBL ESP32"),
      +        FLUIDNC("FluidNC"),
      +        SMOOTHIE("SmoothieBoard"),
      +        TINYG("TinyG"),
      +        G2CORE("g2core"),
      +        XLCD("XLCD"),
      +        LOOPBACK("Loopback"),
      +        LOOPBACK_SLOW("Loopback_Slow");
      +        final String name;
      +        CONTROLLER(String name) {
      +            this.name = name;
      +        }
      ... (+9 more diff lines)
  FILE ugs-core/src/com/willwinder/universalgcodesender/model/GUIBackend.java  (merge_outcome=clean)
    base->ours 2 chg-lines | base->theirs 2 | merged==dev(ws-norm): True
==========================================================================================
MERGE xebia_xebium__a82603c978
  labels: mergiraf=Tests_failed git=Tests_failed spork=Tests_failed parents_pass=True left_par=Tests_passed right_par=Tests_passed test_merge=True
  num_intersecting_files(csv)=2 materialized=1 diverged=0 num_diff_files=19.0
  FILE src/main/java/com/xebia/incubator/xebium/SeleniumDriverFixture.java  (merge_outcome=clean)
    base->ours 13 chg-lines | base->theirs 2 | merged==dev(ws-norm): True
