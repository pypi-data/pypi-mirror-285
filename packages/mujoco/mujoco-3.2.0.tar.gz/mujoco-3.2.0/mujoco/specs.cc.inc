
  // mjSpec
  mjSpec.def_property(
      "modelname",
      [](MjSpec& self) -> std::string_view {
        return *self.ptr->modelname;
      },
      [](MjSpec& self, std::string_view modelname) {
        *(self.ptr->modelname) = modelname;
    });
mjSpec.def_property("autolimits",[](MjSpec& self) -> mjtByte {
        return self.ptr->autolimits;
      },[](MjSpec& self, mjtByte autolimits) {
        self.ptr->autolimits = autolimits;
      });
mjSpec.def_property("boundmass",[](MjSpec& self) -> double {
        return self.ptr->boundmass;
      },[](MjSpec& self, double boundmass) {
        self.ptr->boundmass = boundmass;
      });
mjSpec.def_property("boundinertia",[](MjSpec& self) -> double {
        return self.ptr->boundinertia;
      },[](MjSpec& self, double boundinertia) {
        self.ptr->boundinertia = boundinertia;
      });
mjSpec.def_property("settotalmass",[](MjSpec& self) -> double {
        return self.ptr->settotalmass;
      },[](MjSpec& self, double settotalmass) {
        self.ptr->settotalmass = settotalmass;
      });
mjSpec.def_property("balanceinertia",[](MjSpec& self) -> mjtByte {
        return self.ptr->balanceinertia;
      },[](MjSpec& self, mjtByte balanceinertia) {
        self.ptr->balanceinertia = balanceinertia;
      });
mjSpec.def_property("strippath",[](MjSpec& self) -> mjtByte {
        return self.ptr->strippath;
      },[](MjSpec& self, mjtByte strippath) {
        self.ptr->strippath = strippath;
      });
mjSpec.def_property("fitaabb",[](MjSpec& self) -> mjtByte {
        return self.ptr->fitaabb;
      },[](MjSpec& self, mjtByte fitaabb) {
        self.ptr->fitaabb = fitaabb;
      });
mjSpec.def_property("degree",[](MjSpec& self) -> mjtByte {
        return self.ptr->degree;
      },[](MjSpec& self, mjtByte degree) {
        self.ptr->degree = degree;
      });
  mjSpec.def_property(
    "eulerseq",
    [](MjSpec& self) -> py::array_t<char> {
      return py::array_t<char>(3, self.ptr->eulerseq);
    },
    [](MjSpec& self, py::object rhs) {
      int i = 0;
      for (auto val : rhs) {
        self.ptr->eulerseq[i++] = py::cast<char>(val);
      }
    }, py::return_value_policy::reference_internal);
  mjSpec.def_property(
      "meshdir",
      [](MjSpec& self) -> std::string_view {
        return *self.ptr->meshdir;
      },
      [](MjSpec& self, std::string_view meshdir) {
        *(self.ptr->meshdir) = meshdir;
    });
  mjSpec.def_property(
      "texturedir",
      [](MjSpec& self) -> std::string_view {
        return *self.ptr->texturedir;
      },
      [](MjSpec& self, std::string_view texturedir) {
        *(self.ptr->texturedir) = texturedir;
    });
mjSpec.def_property("discardvisual",[](MjSpec& self) -> mjtByte {
        return self.ptr->discardvisual;
      },[](MjSpec& self, mjtByte discardvisual) {
        self.ptr->discardvisual = discardvisual;
      });
mjSpec.def_property("convexhull",[](MjSpec& self) -> mjtByte {
        return self.ptr->convexhull;
      },[](MjSpec& self, mjtByte convexhull) {
        self.ptr->convexhull = convexhull;
      });
mjSpec.def_property("usethread",[](MjSpec& self) -> mjtByte {
        return self.ptr->usethread;
      },[](MjSpec& self, mjtByte usethread) {
        self.ptr->usethread = usethread;
      });
mjSpec.def_property("fusestatic",[](MjSpec& self) -> mjtByte {
        return self.ptr->fusestatic;
      },[](MjSpec& self, mjtByte fusestatic) {
        self.ptr->fusestatic = fusestatic;
      });
mjSpec.def_property("inertiafromgeom",[](MjSpec& self) -> int {
        return self.ptr->inertiafromgeom;
      },[](MjSpec& self, int inertiafromgeom) {
        self.ptr->inertiafromgeom = inertiafromgeom;
      });
  mjSpec.def_property(
      "inertiagrouprange",
      [](MjSpec& self) -> MjInt2 {
        return MjInt2(self.ptr->inertiagrouprange);
    },
      [](MjSpec& self, MjIntRef2 inertiagrouprange) {
        MjInt2(self.ptr->inertiagrouprange) = inertiagrouprange;
    }, py::return_value_policy::reference_internal);
mjSpec.def_property("exactmeshinertia",[](MjSpec& self) -> mjtByte {
        return self.ptr->exactmeshinertia;
      },[](MjSpec& self, mjtByte exactmeshinertia) {
        self.ptr->exactmeshinertia = exactmeshinertia;
      });
mjSpec.def_property("LRopt",[](MjSpec& self) -> mjLROpt& {
        return self.ptr->LRopt;
      },[](MjSpec& self, mjLROpt& LRopt) {
        self.ptr->LRopt = LRopt;
      },py::return_value_policy::reference_internal);
mjSpec.def_property("option",[](MjSpec& self) -> mjOption& {
        return self.ptr->option;
      },[](MjSpec& self, mjOption& option) {
        self.ptr->option = option;
      },py::return_value_policy::reference_internal);
mjSpec.def_property("visual",[](MjSpec& self) -> mjVisual& {
        return self.ptr->visual;
      },[](MjSpec& self, mjVisual& visual) {
        self.ptr->visual = visual;
      },py::return_value_policy::reference_internal);
mjSpec.def_property("stat",[](MjSpec& self) -> mjStatistic& {
        return self.ptr->stat;
      },[](MjSpec& self, mjStatistic& stat) {
        self.ptr->stat = stat;
      },py::return_value_policy::reference_internal);
mjSpec.def_property("memory",[](MjSpec& self) -> size_t& {
        return self.ptr->memory;
      },[](MjSpec& self, size_t& memory) {
        self.ptr->memory = memory;
      },py::return_value_policy::reference_internal);
mjSpec.def_property("nemax",[](MjSpec& self) -> int {
        return self.ptr->nemax;
      },[](MjSpec& self, int nemax) {
        self.ptr->nemax = nemax;
      });
mjSpec.def_property("nuserdata",[](MjSpec& self) -> int {
        return self.ptr->nuserdata;
      },[](MjSpec& self, int nuserdata) {
        self.ptr->nuserdata = nuserdata;
      });
mjSpec.def_property("nuser_body",[](MjSpec& self) -> int {
        return self.ptr->nuser_body;
      },[](MjSpec& self, int nuser_body) {
        self.ptr->nuser_body = nuser_body;
      });
mjSpec.def_property("nuser_jnt",[](MjSpec& self) -> int {
        return self.ptr->nuser_jnt;
      },[](MjSpec& self, int nuser_jnt) {
        self.ptr->nuser_jnt = nuser_jnt;
      });
mjSpec.def_property("nuser_geom",[](MjSpec& self) -> int {
        return self.ptr->nuser_geom;
      },[](MjSpec& self, int nuser_geom) {
        self.ptr->nuser_geom = nuser_geom;
      });
mjSpec.def_property("nuser_site",[](MjSpec& self) -> int {
        return self.ptr->nuser_site;
      },[](MjSpec& self, int nuser_site) {
        self.ptr->nuser_site = nuser_site;
      });
mjSpec.def_property("nuser_cam",[](MjSpec& self) -> int {
        return self.ptr->nuser_cam;
      },[](MjSpec& self, int nuser_cam) {
        self.ptr->nuser_cam = nuser_cam;
      });
mjSpec.def_property("nuser_tendon",[](MjSpec& self) -> int {
        return self.ptr->nuser_tendon;
      },[](MjSpec& self, int nuser_tendon) {
        self.ptr->nuser_tendon = nuser_tendon;
      });
mjSpec.def_property("nuser_actuator",[](MjSpec& self) -> int {
        return self.ptr->nuser_actuator;
      },[](MjSpec& self, int nuser_actuator) {
        self.ptr->nuser_actuator = nuser_actuator;
      });
mjSpec.def_property("nuser_sensor",[](MjSpec& self) -> int {
        return self.ptr->nuser_sensor;
      },[](MjSpec& self, int nuser_sensor) {
        self.ptr->nuser_sensor = nuser_sensor;
      });
mjSpec.def_property("nkey",[](MjSpec& self) -> int {
        return self.ptr->nkey;
      },[](MjSpec& self, int nkey) {
        self.ptr->nkey = nkey;
      });
mjSpec.def_property("njmax",[](MjSpec& self) -> int {
        return self.ptr->njmax;
      },[](MjSpec& self, int njmax) {
        self.ptr->njmax = njmax;
      });
mjSpec.def_property("nconmax",[](MjSpec& self) -> int {
        return self.ptr->nconmax;
      },[](MjSpec& self, int nconmax) {
        self.ptr->nconmax = nconmax;
      });
mjSpec.def_property("nstack",[](MjSpec& self) -> size_t& {
        return self.ptr->nstack;
      },[](MjSpec& self, size_t& nstack) {
        self.ptr->nstack = nstack;
      },py::return_value_policy::reference_internal);
  mjSpec.def_property(
      "comment",
      [](MjSpec& self) -> std::string_view {
        return *self.ptr->comment;
      },
      [](MjSpec& self, std::string_view comment) {
        *(self.ptr->comment) = comment;
    });
  mjSpec.def_property(
      "modelfiledir",
      [](MjSpec& self) -> std::string_view {
        return *self.ptr->modelfiledir;
      },
      [](MjSpec& self, std::string_view modelfiledir) {
        *(self.ptr->modelfiledir) = modelfiledir;
    });
mjSpec.def_property("hasImplicitPluginElem",[](MjSpec& self) -> mjtByte {
        return self.ptr->hasImplicitPluginElem;
      },[](MjSpec& self, mjtByte hasImplicitPluginElem) {
        self.ptr->hasImplicitPluginElem = hasImplicitPluginElem;
      });

  // mjsOrientation
mjsOrientation.def_property("type",[](raw::MjsOrientation& self) -> mjtOrientation& {
        return self.type;
      },[](raw::MjsOrientation& self, mjtOrientation& type) {
        self.type = type;
      },py::return_value_policy::reference_internal);
  mjsOrientation.def_property(
      "axisangle",
      [](raw::MjsOrientation& self) -> MjDouble4 {
        return MjDouble4(self.axisangle);
    },
      [](raw::MjsOrientation& self, MjDoubleRef4 axisangle) {
        MjDouble4(self.axisangle) = axisangle;
    }, py::return_value_policy::reference_internal);
  mjsOrientation.def_property(
      "xyaxes",
      [](raw::MjsOrientation& self) -> MjDouble6 {
        return MjDouble6(self.xyaxes);
    },
      [](raw::MjsOrientation& self, MjDoubleRef6 xyaxes) {
        MjDouble6(self.xyaxes) = xyaxes;
    }, py::return_value_policy::reference_internal);
  mjsOrientation.def_property(
      "zaxis",
      [](raw::MjsOrientation& self) -> MjDouble3 {
        return MjDouble3(self.zaxis);
    },
      [](raw::MjsOrientation& self, MjDoubleRef3 zaxis) {
        MjDouble3(self.zaxis) = zaxis;
    }, py::return_value_policy::reference_internal);
  mjsOrientation.def_property(
      "euler",
      [](raw::MjsOrientation& self) -> MjDouble3 {
        return MjDouble3(self.euler);
    },
      [](raw::MjsOrientation& self, MjDoubleRef3 euler) {
        MjDouble3(self.euler) = euler;
    }, py::return_value_policy::reference_internal);

  // mjsPlugin
  mjsPlugin.def_property(
      "name",
      [](raw::MjsPlugin& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsPlugin& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsPlugin.def_property(
      "instance_name",
      [](raw::MjsPlugin& self) -> std::string_view {
        return *self.instance_name;
      },
      [](raw::MjsPlugin& self, std::string_view instance_name) {
        *(self.instance_name) = instance_name;
    });
mjsPlugin.def_property("plugin_slot",[](raw::MjsPlugin& self) -> int {
        return self.plugin_slot;
      },[](raw::MjsPlugin& self, int plugin_slot) {
        self.plugin_slot = plugin_slot;
      });
mjsPlugin.def_property("active",[](raw::MjsPlugin& self) -> mjtByte {
        return self.active;
      },[](raw::MjsPlugin& self, mjtByte active) {
        self.active = active;
      });
  mjsPlugin.def_property(
      "info",
      [](raw::MjsPlugin& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsPlugin& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsBody
  mjsBody.def_property(
      "name",
      [](raw::MjsBody& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsBody& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsBody.def_property(
      "childclass",
      [](raw::MjsBody& self) -> std::string_view {
        return *self.childclass;
      },
      [](raw::MjsBody& self, std::string_view childclass) {
        *(self.childclass) = childclass;
    });
  mjsBody.def_property(
      "pos",
      [](raw::MjsBody& self) -> MjDouble3 {
        return MjDouble3(self.pos);
    },
      [](raw::MjsBody& self, MjDoubleRef3 pos) {
        MjDouble3(self.pos) = pos;
    }, py::return_value_policy::reference_internal);
  mjsBody.def_property(
      "quat",
      [](raw::MjsBody& self) -> MjDouble4 {
        return MjDouble4(self.quat);
    },
      [](raw::MjsBody& self, MjDoubleRef4 quat) {
        MjDouble4(self.quat) = quat;
    }, py::return_value_policy::reference_internal);
mjsBody.def_property("alt",[](raw::MjsBody& self) -> raw::MjsOrientation {
        return self.alt;
      },[](raw::MjsBody& self, raw::MjsOrientation alt) {
        self.alt = alt;
      },py::return_value_policy::reference_internal);
mjsBody.def_property("mass",[](raw::MjsBody& self) -> double {
        return self.mass;
      },[](raw::MjsBody& self, double mass) {
        self.mass = mass;
      });
  mjsBody.def_property(
      "ipos",
      [](raw::MjsBody& self) -> MjDouble3 {
        return MjDouble3(self.ipos);
    },
      [](raw::MjsBody& self, MjDoubleRef3 ipos) {
        MjDouble3(self.ipos) = ipos;
    }, py::return_value_policy::reference_internal);
  mjsBody.def_property(
      "iquat",
      [](raw::MjsBody& self) -> MjDouble4 {
        return MjDouble4(self.iquat);
    },
      [](raw::MjsBody& self, MjDoubleRef4 iquat) {
        MjDouble4(self.iquat) = iquat;
    }, py::return_value_policy::reference_internal);
  mjsBody.def_property(
      "inertia",
      [](raw::MjsBody& self) -> MjDouble3 {
        return MjDouble3(self.inertia);
    },
      [](raw::MjsBody& self, MjDoubleRef3 inertia) {
        MjDouble3(self.inertia) = inertia;
    }, py::return_value_policy::reference_internal);
mjsBody.def_property("ialt",[](raw::MjsBody& self) -> raw::MjsOrientation {
        return self.ialt;
      },[](raw::MjsBody& self, raw::MjsOrientation ialt) {
        self.ialt = ialt;
      },py::return_value_policy::reference_internal);
  mjsBody.def_property(
      "fullinertia",
      [](raw::MjsBody& self) -> MjDouble6 {
        return MjDouble6(self.fullinertia);
    },
      [](raw::MjsBody& self, MjDoubleRef6 fullinertia) {
        MjDouble6(self.fullinertia) = fullinertia;
    }, py::return_value_policy::reference_internal);
mjsBody.def_property("mocap",[](raw::MjsBody& self) -> mjtByte {
        return self.mocap;
      },[](raw::MjsBody& self, mjtByte mocap) {
        self.mocap = mocap;
      });
mjsBody.def_property("gravcomp",[](raw::MjsBody& self) -> double {
        return self.gravcomp;
      },[](raw::MjsBody& self, double gravcomp) {
        self.gravcomp = gravcomp;
      });
  mjsBody.def_property(
    "userdata",
    [](raw::MjsBody& self) -> py::array_t<double> {
        return py::array_t<double>(self.userdata->size(),
                                      self.userdata->data());
      },
    [](raw::MjsBody& self, py::object rhs) {
        self.userdata->clear();
        self.userdata->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.userdata->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
mjsBody.def_property("explicitinertial",[](raw::MjsBody& self) -> mjtByte {
        return self.explicitinertial;
      },[](raw::MjsBody& self, mjtByte explicitinertial) {
        self.explicitinertial = explicitinertial;
      });
mjsBody.def_property("plugin",[](raw::MjsBody& self) -> raw::MjsPlugin {
        return self.plugin;
      },[](raw::MjsBody& self, raw::MjsPlugin plugin) {
        self.plugin = plugin;
      },py::return_value_policy::reference_internal);
  mjsBody.def_property(
      "info",
      [](raw::MjsBody& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsBody& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsFrame
  mjsFrame.def_property(
      "name",
      [](raw::MjsFrame& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsFrame& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsFrame.def_property(
      "childclass",
      [](raw::MjsFrame& self) -> std::string_view {
        return *self.childclass;
      },
      [](raw::MjsFrame& self, std::string_view childclass) {
        *(self.childclass) = childclass;
    });
  mjsFrame.def_property(
      "pos",
      [](raw::MjsFrame& self) -> MjDouble3 {
        return MjDouble3(self.pos);
    },
      [](raw::MjsFrame& self, MjDoubleRef3 pos) {
        MjDouble3(self.pos) = pos;
    }, py::return_value_policy::reference_internal);
  mjsFrame.def_property(
      "quat",
      [](raw::MjsFrame& self) -> MjDouble4 {
        return MjDouble4(self.quat);
    },
      [](raw::MjsFrame& self, MjDoubleRef4 quat) {
        MjDouble4(self.quat) = quat;
    }, py::return_value_policy::reference_internal);
mjsFrame.def_property("alt",[](raw::MjsFrame& self) -> raw::MjsOrientation {
        return self.alt;
      },[](raw::MjsFrame& self, raw::MjsOrientation alt) {
        self.alt = alt;
      },py::return_value_policy::reference_internal);
  mjsFrame.def_property(
      "info",
      [](raw::MjsFrame& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsFrame& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsJoint
  mjsJoint.def_property(
      "name",
      [](raw::MjsJoint& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsJoint& self, std::string_view name) {
        *(self.name) = name;
    });
mjsJoint.def_property("type",[](raw::MjsJoint& self) -> mjtJoint& {
        return self.type;
      },[](raw::MjsJoint& self, mjtJoint& type) {
        self.type = type;
      },py::return_value_policy::reference_internal);
  mjsJoint.def_property(
      "pos",
      [](raw::MjsJoint& self) -> MjDouble3 {
        return MjDouble3(self.pos);
    },
      [](raw::MjsJoint& self, MjDoubleRef3 pos) {
        MjDouble3(self.pos) = pos;
    }, py::return_value_policy::reference_internal);
  mjsJoint.def_property(
      "axis",
      [](raw::MjsJoint& self) -> MjDouble3 {
        return MjDouble3(self.axis);
    },
      [](raw::MjsJoint& self, MjDoubleRef3 axis) {
        MjDouble3(self.axis) = axis;
    }, py::return_value_policy::reference_internal);
mjsJoint.def_property("ref",[](raw::MjsJoint& self) -> double {
        return self.ref;
      },[](raw::MjsJoint& self, double ref) {
        self.ref = ref;
      });
mjsJoint.def_property("stiffness",[](raw::MjsJoint& self) -> double {
        return self.stiffness;
      },[](raw::MjsJoint& self, double stiffness) {
        self.stiffness = stiffness;
      });
mjsJoint.def_property("springref",[](raw::MjsJoint& self) -> double {
        return self.springref;
      },[](raw::MjsJoint& self, double springref) {
        self.springref = springref;
      });
  mjsJoint.def_property(
      "springdamper",
      [](raw::MjsJoint& self) -> MjDouble2 {
        return MjDouble2(self.springdamper);
    },
      [](raw::MjsJoint& self, MjDoubleRef2 springdamper) {
        MjDouble2(self.springdamper) = springdamper;
    }, py::return_value_policy::reference_internal);
mjsJoint.def_property("limited",[](raw::MjsJoint& self) -> int {
        return self.limited;
      },[](raw::MjsJoint& self, int limited) {
        self.limited = limited;
      });
  mjsJoint.def_property(
      "range",
      [](raw::MjsJoint& self) -> MjDouble2 {
        return MjDouble2(self.range);
    },
      [](raw::MjsJoint& self, MjDoubleRef2 range) {
        MjDouble2(self.range) = range;
    }, py::return_value_policy::reference_internal);
mjsJoint.def_property("margin",[](raw::MjsJoint& self) -> double {
        return self.margin;
      },[](raw::MjsJoint& self, double margin) {
        self.margin = margin;
      });
  mjsJoint.def_property(
      "solref_limit",
      [](raw::MjsJoint& self) -> MjDouble2 {
        return MjDouble2(self.solref_limit);
    },
      [](raw::MjsJoint& self, MjDoubleRef2 solref_limit) {
        MjDouble2(self.solref_limit) = solref_limit;
    }, py::return_value_policy::reference_internal);
  mjsJoint.def_property(
      "solimp_limit",
      [](raw::MjsJoint& self) -> MjDouble5 {
        return MjDouble5(self.solimp_limit);
    },
      [](raw::MjsJoint& self, MjDoubleRef5 solimp_limit) {
        MjDouble5(self.solimp_limit) = solimp_limit;
    }, py::return_value_policy::reference_internal);
mjsJoint.def_property("actfrclimited",[](raw::MjsJoint& self) -> int {
        return self.actfrclimited;
      },[](raw::MjsJoint& self, int actfrclimited) {
        self.actfrclimited = actfrclimited;
      });
  mjsJoint.def_property(
      "actfrcrange",
      [](raw::MjsJoint& self) -> MjDouble2 {
        return MjDouble2(self.actfrcrange);
    },
      [](raw::MjsJoint& self, MjDoubleRef2 actfrcrange) {
        MjDouble2(self.actfrcrange) = actfrcrange;
    }, py::return_value_policy::reference_internal);
mjsJoint.def_property("armature",[](raw::MjsJoint& self) -> double {
        return self.armature;
      },[](raw::MjsJoint& self, double armature) {
        self.armature = armature;
      });
mjsJoint.def_property("damping",[](raw::MjsJoint& self) -> double {
        return self.damping;
      },[](raw::MjsJoint& self, double damping) {
        self.damping = damping;
      });
mjsJoint.def_property("frictionloss",[](raw::MjsJoint& self) -> double {
        return self.frictionloss;
      },[](raw::MjsJoint& self, double frictionloss) {
        self.frictionloss = frictionloss;
      });
  mjsJoint.def_property(
      "solref_friction",
      [](raw::MjsJoint& self) -> MjDouble2 {
        return MjDouble2(self.solref_friction);
    },
      [](raw::MjsJoint& self, MjDoubleRef2 solref_friction) {
        MjDouble2(self.solref_friction) = solref_friction;
    }, py::return_value_policy::reference_internal);
  mjsJoint.def_property(
      "solimp_friction",
      [](raw::MjsJoint& self) -> MjDouble5 {
        return MjDouble5(self.solimp_friction);
    },
      [](raw::MjsJoint& self, MjDoubleRef5 solimp_friction) {
        MjDouble5(self.solimp_friction) = solimp_friction;
    }, py::return_value_policy::reference_internal);
mjsJoint.def_property("group",[](raw::MjsJoint& self) -> int {
        return self.group;
      },[](raw::MjsJoint& self, int group) {
        self.group = group;
      });
mjsJoint.def_property("actgravcomp",[](raw::MjsJoint& self) -> mjtByte {
        return self.actgravcomp;
      },[](raw::MjsJoint& self, mjtByte actgravcomp) {
        self.actgravcomp = actgravcomp;
      });
  mjsJoint.def_property(
    "userdata",
    [](raw::MjsJoint& self) -> py::array_t<double> {
        return py::array_t<double>(self.userdata->size(),
                                      self.userdata->data());
      },
    [](raw::MjsJoint& self, py::object rhs) {
        self.userdata->clear();
        self.userdata->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.userdata->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsJoint.def_property(
      "info",
      [](raw::MjsJoint& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsJoint& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsGeom
  mjsGeom.def_property(
      "name",
      [](raw::MjsGeom& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsGeom& self, std::string_view name) {
        *(self.name) = name;
    });
mjsGeom.def_property("type",[](raw::MjsGeom& self) -> mjtGeom& {
        return self.type;
      },[](raw::MjsGeom& self, mjtGeom& type) {
        self.type = type;
      },py::return_value_policy::reference_internal);
  mjsGeom.def_property(
      "pos",
      [](raw::MjsGeom& self) -> MjDouble3 {
        return MjDouble3(self.pos);
    },
      [](raw::MjsGeom& self, MjDoubleRef3 pos) {
        MjDouble3(self.pos) = pos;
    }, py::return_value_policy::reference_internal);
  mjsGeom.def_property(
      "quat",
      [](raw::MjsGeom& self) -> MjDouble4 {
        return MjDouble4(self.quat);
    },
      [](raw::MjsGeom& self, MjDoubleRef4 quat) {
        MjDouble4(self.quat) = quat;
    }, py::return_value_policy::reference_internal);
mjsGeom.def_property("alt",[](raw::MjsGeom& self) -> raw::MjsOrientation {
        return self.alt;
      },[](raw::MjsGeom& self, raw::MjsOrientation alt) {
        self.alt = alt;
      },py::return_value_policy::reference_internal);
  mjsGeom.def_property(
      "fromto",
      [](raw::MjsGeom& self) -> MjDouble6 {
        return MjDouble6(self.fromto);
    },
      [](raw::MjsGeom& self, MjDoubleRef6 fromto) {
        MjDouble6(self.fromto) = fromto;
    }, py::return_value_policy::reference_internal);
  mjsGeom.def_property(
      "size",
      [](raw::MjsGeom& self) -> MjDouble3 {
        return MjDouble3(self.size);
    },
      [](raw::MjsGeom& self, MjDoubleRef3 size) {
        MjDouble3(self.size) = size;
    }, py::return_value_policy::reference_internal);
mjsGeom.def_property("contype",[](raw::MjsGeom& self) -> int {
        return self.contype;
      },[](raw::MjsGeom& self, int contype) {
        self.contype = contype;
      });
mjsGeom.def_property("conaffinity",[](raw::MjsGeom& self) -> int {
        return self.conaffinity;
      },[](raw::MjsGeom& self, int conaffinity) {
        self.conaffinity = conaffinity;
      });
mjsGeom.def_property("condim",[](raw::MjsGeom& self) -> int {
        return self.condim;
      },[](raw::MjsGeom& self, int condim) {
        self.condim = condim;
      });
mjsGeom.def_property("priority",[](raw::MjsGeom& self) -> int {
        return self.priority;
      },[](raw::MjsGeom& self, int priority) {
        self.priority = priority;
      });
  mjsGeom.def_property(
      "friction",
      [](raw::MjsGeom& self) -> MjDouble3 {
        return MjDouble3(self.friction);
    },
      [](raw::MjsGeom& self, MjDoubleRef3 friction) {
        MjDouble3(self.friction) = friction;
    }, py::return_value_policy::reference_internal);
mjsGeom.def_property("solmix",[](raw::MjsGeom& self) -> double {
        return self.solmix;
      },[](raw::MjsGeom& self, double solmix) {
        self.solmix = solmix;
      });
  mjsGeom.def_property(
      "solref",
      [](raw::MjsGeom& self) -> MjDouble2 {
        return MjDouble2(self.solref);
    },
      [](raw::MjsGeom& self, MjDoubleRef2 solref) {
        MjDouble2(self.solref) = solref;
    }, py::return_value_policy::reference_internal);
  mjsGeom.def_property(
      "solimp",
      [](raw::MjsGeom& self) -> MjDouble5 {
        return MjDouble5(self.solimp);
    },
      [](raw::MjsGeom& self, MjDoubleRef5 solimp) {
        MjDouble5(self.solimp) = solimp;
    }, py::return_value_policy::reference_internal);
mjsGeom.def_property("margin",[](raw::MjsGeom& self) -> double {
        return self.margin;
      },[](raw::MjsGeom& self, double margin) {
        self.margin = margin;
      });
mjsGeom.def_property("gap",[](raw::MjsGeom& self) -> double {
        return self.gap;
      },[](raw::MjsGeom& self, double gap) {
        self.gap = gap;
      });
mjsGeom.def_property("mass",[](raw::MjsGeom& self) -> double {
        return self.mass;
      },[](raw::MjsGeom& self, double mass) {
        self.mass = mass;
      });
mjsGeom.def_property("density",[](raw::MjsGeom& self) -> double {
        return self.density;
      },[](raw::MjsGeom& self, double density) {
        self.density = density;
      });
mjsGeom.def_property("typeinertia",[](raw::MjsGeom& self) -> mjtGeomInertia& {
        return self.typeinertia;
      },[](raw::MjsGeom& self, mjtGeomInertia& typeinertia) {
        self.typeinertia = typeinertia;
      },py::return_value_policy::reference_internal);
mjsGeom.def_property("fluid_ellipsoid",[](raw::MjsGeom& self) -> mjtNum {
        return self.fluid_ellipsoid;
      },[](raw::MjsGeom& self, mjtNum fluid_ellipsoid) {
        self.fluid_ellipsoid = fluid_ellipsoid;
      });
  mjsGeom.def_property(
      "fluid_coefs",
      [](raw::MjsGeom& self) -> MjDouble5 {
        return MjDouble5(self.fluid_coefs);
    },
      [](raw::MjsGeom& self, MjDoubleRef5 fluid_coefs) {
        MjDouble5(self.fluid_coefs) = fluid_coefs;
    }, py::return_value_policy::reference_internal);
  mjsGeom.def_property(
      "material",
      [](raw::MjsGeom& self) -> std::string_view {
        return *self.material;
      },
      [](raw::MjsGeom& self, std::string_view material) {
        *(self.material) = material;
    });
  mjsGeom.def_property(
      "rgba",
      [](raw::MjsGeom& self) -> MjFloat4 {
        return MjFloat4(self.rgba);
    },
      [](raw::MjsGeom& self, MjFloatRef4 rgba) {
        MjFloat4(self.rgba) = rgba;
    }, py::return_value_policy::reference_internal);
mjsGeom.def_property("group",[](raw::MjsGeom& self) -> int {
        return self.group;
      },[](raw::MjsGeom& self, int group) {
        self.group = group;
      });
  mjsGeom.def_property(
      "hfieldname",
      [](raw::MjsGeom& self) -> std::string_view {
        return *self.hfieldname;
      },
      [](raw::MjsGeom& self, std::string_view hfieldname) {
        *(self.hfieldname) = hfieldname;
    });
  mjsGeom.def_property(
      "meshname",
      [](raw::MjsGeom& self) -> std::string_view {
        return *self.meshname;
      },
      [](raw::MjsGeom& self, std::string_view meshname) {
        *(self.meshname) = meshname;
    });
mjsGeom.def_property("fitscale",[](raw::MjsGeom& self) -> double {
        return self.fitscale;
      },[](raw::MjsGeom& self, double fitscale) {
        self.fitscale = fitscale;
      });
  mjsGeom.def_property(
    "userdata",
    [](raw::MjsGeom& self) -> py::array_t<double> {
        return py::array_t<double>(self.userdata->size(),
                                      self.userdata->data());
      },
    [](raw::MjsGeom& self, py::object rhs) {
        self.userdata->clear();
        self.userdata->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.userdata->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
mjsGeom.def_property("plugin",[](raw::MjsGeom& self) -> raw::MjsPlugin {
        return self.plugin;
      },[](raw::MjsGeom& self, raw::MjsPlugin plugin) {
        self.plugin = plugin;
      },py::return_value_policy::reference_internal);
  mjsGeom.def_property(
      "info",
      [](raw::MjsGeom& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsGeom& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsSite
  mjsSite.def_property(
      "name",
      [](raw::MjsSite& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsSite& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsSite.def_property(
      "pos",
      [](raw::MjsSite& self) -> MjDouble3 {
        return MjDouble3(self.pos);
    },
      [](raw::MjsSite& self, MjDoubleRef3 pos) {
        MjDouble3(self.pos) = pos;
    }, py::return_value_policy::reference_internal);
  mjsSite.def_property(
      "quat",
      [](raw::MjsSite& self) -> MjDouble4 {
        return MjDouble4(self.quat);
    },
      [](raw::MjsSite& self, MjDoubleRef4 quat) {
        MjDouble4(self.quat) = quat;
    }, py::return_value_policy::reference_internal);
mjsSite.def_property("alt",[](raw::MjsSite& self) -> raw::MjsOrientation {
        return self.alt;
      },[](raw::MjsSite& self, raw::MjsOrientation alt) {
        self.alt = alt;
      },py::return_value_policy::reference_internal);
  mjsSite.def_property(
      "fromto",
      [](raw::MjsSite& self) -> MjDouble6 {
        return MjDouble6(self.fromto);
    },
      [](raw::MjsSite& self, MjDoubleRef6 fromto) {
        MjDouble6(self.fromto) = fromto;
    }, py::return_value_policy::reference_internal);
  mjsSite.def_property(
      "size",
      [](raw::MjsSite& self) -> MjDouble3 {
        return MjDouble3(self.size);
    },
      [](raw::MjsSite& self, MjDoubleRef3 size) {
        MjDouble3(self.size) = size;
    }, py::return_value_policy::reference_internal);
mjsSite.def_property("type",[](raw::MjsSite& self) -> mjtGeom& {
        return self.type;
      },[](raw::MjsSite& self, mjtGeom& type) {
        self.type = type;
      },py::return_value_policy::reference_internal);
  mjsSite.def_property(
      "material",
      [](raw::MjsSite& self) -> std::string_view {
        return *self.material;
      },
      [](raw::MjsSite& self, std::string_view material) {
        *(self.material) = material;
    });
mjsSite.def_property("group",[](raw::MjsSite& self) -> int {
        return self.group;
      },[](raw::MjsSite& self, int group) {
        self.group = group;
      });
  mjsSite.def_property(
      "rgba",
      [](raw::MjsSite& self) -> MjFloat4 {
        return MjFloat4(self.rgba);
    },
      [](raw::MjsSite& self, MjFloatRef4 rgba) {
        MjFloat4(self.rgba) = rgba;
    }, py::return_value_policy::reference_internal);
  mjsSite.def_property(
    "userdata",
    [](raw::MjsSite& self) -> py::array_t<double> {
        return py::array_t<double>(self.userdata->size(),
                                      self.userdata->data());
      },
    [](raw::MjsSite& self, py::object rhs) {
        self.userdata->clear();
        self.userdata->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.userdata->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsSite.def_property(
      "info",
      [](raw::MjsSite& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsSite& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsCamera
  mjsCamera.def_property(
      "name",
      [](raw::MjsCamera& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsCamera& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsCamera.def_property(
      "pos",
      [](raw::MjsCamera& self) -> MjDouble3 {
        return MjDouble3(self.pos);
    },
      [](raw::MjsCamera& self, MjDoubleRef3 pos) {
        MjDouble3(self.pos) = pos;
    }, py::return_value_policy::reference_internal);
  mjsCamera.def_property(
      "quat",
      [](raw::MjsCamera& self) -> MjDouble4 {
        return MjDouble4(self.quat);
    },
      [](raw::MjsCamera& self, MjDoubleRef4 quat) {
        MjDouble4(self.quat) = quat;
    }, py::return_value_policy::reference_internal);
mjsCamera.def_property("alt",[](raw::MjsCamera& self) -> raw::MjsOrientation {
        return self.alt;
      },[](raw::MjsCamera& self, raw::MjsOrientation alt) {
        self.alt = alt;
      },py::return_value_policy::reference_internal);
mjsCamera.def_property("mode",[](raw::MjsCamera& self) -> mjtCamLight& {
        return self.mode;
      },[](raw::MjsCamera& self, mjtCamLight& mode) {
        self.mode = mode;
      },py::return_value_policy::reference_internal);
  mjsCamera.def_property(
      "targetbody",
      [](raw::MjsCamera& self) -> std::string_view {
        return *self.targetbody;
      },
      [](raw::MjsCamera& self, std::string_view targetbody) {
        *(self.targetbody) = targetbody;
    });
mjsCamera.def_property("orthographic",[](raw::MjsCamera& self) -> int {
        return self.orthographic;
      },[](raw::MjsCamera& self, int orthographic) {
        self.orthographic = orthographic;
      });
mjsCamera.def_property("fovy",[](raw::MjsCamera& self) -> double {
        return self.fovy;
      },[](raw::MjsCamera& self, double fovy) {
        self.fovy = fovy;
      });
mjsCamera.def_property("ipd",[](raw::MjsCamera& self) -> double {
        return self.ipd;
      },[](raw::MjsCamera& self, double ipd) {
        self.ipd = ipd;
      });
  mjsCamera.def_property(
      "intrinsic",
      [](raw::MjsCamera& self) -> MjFloat4 {
        return MjFloat4(self.intrinsic);
    },
      [](raw::MjsCamera& self, MjFloatRef4 intrinsic) {
        MjFloat4(self.intrinsic) = intrinsic;
    }, py::return_value_policy::reference_internal);
  mjsCamera.def_property(
      "sensor_size",
      [](raw::MjsCamera& self) -> MjFloat2 {
        return MjFloat2(self.sensor_size);
    },
      [](raw::MjsCamera& self, MjFloatRef2 sensor_size) {
        MjFloat2(self.sensor_size) = sensor_size;
    }, py::return_value_policy::reference_internal);
  mjsCamera.def_property(
      "resolution",
      [](raw::MjsCamera& self) -> MjFloat2 {
        return MjFloat2(self.resolution);
    },
      [](raw::MjsCamera& self, MjFloatRef2 resolution) {
        MjFloat2(self.resolution) = resolution;
    }, py::return_value_policy::reference_internal);
  mjsCamera.def_property(
      "focal_length",
      [](raw::MjsCamera& self) -> MjFloat2 {
        return MjFloat2(self.focal_length);
    },
      [](raw::MjsCamera& self, MjFloatRef2 focal_length) {
        MjFloat2(self.focal_length) = focal_length;
    }, py::return_value_policy::reference_internal);
  mjsCamera.def_property(
      "focal_pixel",
      [](raw::MjsCamera& self) -> MjFloat2 {
        return MjFloat2(self.focal_pixel);
    },
      [](raw::MjsCamera& self, MjFloatRef2 focal_pixel) {
        MjFloat2(self.focal_pixel) = focal_pixel;
    }, py::return_value_policy::reference_internal);
  mjsCamera.def_property(
      "principal_length",
      [](raw::MjsCamera& self) -> MjFloat2 {
        return MjFloat2(self.principal_length);
    },
      [](raw::MjsCamera& self, MjFloatRef2 principal_length) {
        MjFloat2(self.principal_length) = principal_length;
    }, py::return_value_policy::reference_internal);
  mjsCamera.def_property(
      "principal_pixel",
      [](raw::MjsCamera& self) -> MjFloat2 {
        return MjFloat2(self.principal_pixel);
    },
      [](raw::MjsCamera& self, MjFloatRef2 principal_pixel) {
        MjFloat2(self.principal_pixel) = principal_pixel;
    }, py::return_value_policy::reference_internal);
  mjsCamera.def_property(
    "userdata",
    [](raw::MjsCamera& self) -> py::array_t<double> {
        return py::array_t<double>(self.userdata->size(),
                                      self.userdata->data());
      },
    [](raw::MjsCamera& self, py::object rhs) {
        self.userdata->clear();
        self.userdata->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.userdata->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsCamera.def_property(
      "info",
      [](raw::MjsCamera& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsCamera& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsLight
  mjsLight.def_property(
      "name",
      [](raw::MjsLight& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsLight& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsLight.def_property(
      "pos",
      [](raw::MjsLight& self) -> MjDouble3 {
        return MjDouble3(self.pos);
    },
      [](raw::MjsLight& self, MjDoubleRef3 pos) {
        MjDouble3(self.pos) = pos;
    }, py::return_value_policy::reference_internal);
  mjsLight.def_property(
      "dir",
      [](raw::MjsLight& self) -> MjDouble3 {
        return MjDouble3(self.dir);
    },
      [](raw::MjsLight& self, MjDoubleRef3 dir) {
        MjDouble3(self.dir) = dir;
    }, py::return_value_policy::reference_internal);
mjsLight.def_property("mode",[](raw::MjsLight& self) -> mjtCamLight& {
        return self.mode;
      },[](raw::MjsLight& self, mjtCamLight& mode) {
        self.mode = mode;
      },py::return_value_policy::reference_internal);
  mjsLight.def_property(
      "targetbody",
      [](raw::MjsLight& self) -> std::string_view {
        return *self.targetbody;
      },
      [](raw::MjsLight& self, std::string_view targetbody) {
        *(self.targetbody) = targetbody;
    });
mjsLight.def_property("active",[](raw::MjsLight& self) -> mjtByte {
        return self.active;
      },[](raw::MjsLight& self, mjtByte active) {
        self.active = active;
      });
mjsLight.def_property("directional",[](raw::MjsLight& self) -> mjtByte {
        return self.directional;
      },[](raw::MjsLight& self, mjtByte directional) {
        self.directional = directional;
      });
mjsLight.def_property("castshadow",[](raw::MjsLight& self) -> mjtByte {
        return self.castshadow;
      },[](raw::MjsLight& self, mjtByte castshadow) {
        self.castshadow = castshadow;
      });
mjsLight.def_property("bulbradius",[](raw::MjsLight& self) -> double {
        return self.bulbradius;
      },[](raw::MjsLight& self, double bulbradius) {
        self.bulbradius = bulbradius;
      });
  mjsLight.def_property(
      "attenuation",
      [](raw::MjsLight& self) -> MjFloat3 {
        return MjFloat3(self.attenuation);
    },
      [](raw::MjsLight& self, MjFloatRef3 attenuation) {
        MjFloat3(self.attenuation) = attenuation;
    }, py::return_value_policy::reference_internal);
mjsLight.def_property("cutoff",[](raw::MjsLight& self) -> float {
        return self.cutoff;
      },[](raw::MjsLight& self, float cutoff) {
        self.cutoff = cutoff;
      });
mjsLight.def_property("exponent",[](raw::MjsLight& self) -> float {
        return self.exponent;
      },[](raw::MjsLight& self, float exponent) {
        self.exponent = exponent;
      });
  mjsLight.def_property(
      "ambient",
      [](raw::MjsLight& self) -> MjFloat3 {
        return MjFloat3(self.ambient);
    },
      [](raw::MjsLight& self, MjFloatRef3 ambient) {
        MjFloat3(self.ambient) = ambient;
    }, py::return_value_policy::reference_internal);
  mjsLight.def_property(
      "diffuse",
      [](raw::MjsLight& self) -> MjFloat3 {
        return MjFloat3(self.diffuse);
    },
      [](raw::MjsLight& self, MjFloatRef3 diffuse) {
        MjFloat3(self.diffuse) = diffuse;
    }, py::return_value_policy::reference_internal);
  mjsLight.def_property(
      "specular",
      [](raw::MjsLight& self) -> MjFloat3 {
        return MjFloat3(self.specular);
    },
      [](raw::MjsLight& self, MjFloatRef3 specular) {
        MjFloat3(self.specular) = specular;
    }, py::return_value_policy::reference_internal);
  mjsLight.def_property(
      "info",
      [](raw::MjsLight& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsLight& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsFlex
  mjsFlex.def_property(
      "name",
      [](raw::MjsFlex& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsFlex& self, std::string_view name) {
        *(self.name) = name;
    });
mjsFlex.def_property("contype",[](raw::MjsFlex& self) -> int {
        return self.contype;
      },[](raw::MjsFlex& self, int contype) {
        self.contype = contype;
      });
mjsFlex.def_property("conaffinity",[](raw::MjsFlex& self) -> int {
        return self.conaffinity;
      },[](raw::MjsFlex& self, int conaffinity) {
        self.conaffinity = conaffinity;
      });
mjsFlex.def_property("condim",[](raw::MjsFlex& self) -> int {
        return self.condim;
      },[](raw::MjsFlex& self, int condim) {
        self.condim = condim;
      });
mjsFlex.def_property("priority",[](raw::MjsFlex& self) -> int {
        return self.priority;
      },[](raw::MjsFlex& self, int priority) {
        self.priority = priority;
      });
  mjsFlex.def_property(
      "friction",
      [](raw::MjsFlex& self) -> MjDouble3 {
        return MjDouble3(self.friction);
    },
      [](raw::MjsFlex& self, MjDoubleRef3 friction) {
        MjDouble3(self.friction) = friction;
    }, py::return_value_policy::reference_internal);
mjsFlex.def_property("solmix",[](raw::MjsFlex& self) -> double {
        return self.solmix;
      },[](raw::MjsFlex& self, double solmix) {
        self.solmix = solmix;
      });
  mjsFlex.def_property(
      "solref",
      [](raw::MjsFlex& self) -> MjDouble2 {
        return MjDouble2(self.solref);
    },
      [](raw::MjsFlex& self, MjDoubleRef2 solref) {
        MjDouble2(self.solref) = solref;
    }, py::return_value_policy::reference_internal);
  mjsFlex.def_property(
      "solimp",
      [](raw::MjsFlex& self) -> MjDouble5 {
        return MjDouble5(self.solimp);
    },
      [](raw::MjsFlex& self, MjDoubleRef5 solimp) {
        MjDouble5(self.solimp) = solimp;
    }, py::return_value_policy::reference_internal);
mjsFlex.def_property("margin",[](raw::MjsFlex& self) -> double {
        return self.margin;
      },[](raw::MjsFlex& self, double margin) {
        self.margin = margin;
      });
mjsFlex.def_property("gap",[](raw::MjsFlex& self) -> double {
        return self.gap;
      },[](raw::MjsFlex& self, double gap) {
        self.gap = gap;
      });
mjsFlex.def_property("dim",[](raw::MjsFlex& self) -> int {
        return self.dim;
      },[](raw::MjsFlex& self, int dim) {
        self.dim = dim;
      });
mjsFlex.def_property("radius",[](raw::MjsFlex& self) -> double {
        return self.radius;
      },[](raw::MjsFlex& self, double radius) {
        self.radius = radius;
      });
mjsFlex.def_property("internal",[](raw::MjsFlex& self) -> mjtByte {
        return self.internal;
      },[](raw::MjsFlex& self, mjtByte internal) {
        self.internal = internal;
      });
mjsFlex.def_property("flatskin",[](raw::MjsFlex& self) -> mjtByte {
        return self.flatskin;
      },[](raw::MjsFlex& self, mjtByte flatskin) {
        self.flatskin = flatskin;
      });
mjsFlex.def_property("selfcollide",[](raw::MjsFlex& self) -> int {
        return self.selfcollide;
      },[](raw::MjsFlex& self, int selfcollide) {
        self.selfcollide = selfcollide;
      });
mjsFlex.def_property("activelayers",[](raw::MjsFlex& self) -> int {
        return self.activelayers;
      },[](raw::MjsFlex& self, int activelayers) {
        self.activelayers = activelayers;
      });
mjsFlex.def_property("group",[](raw::MjsFlex& self) -> int {
        return self.group;
      },[](raw::MjsFlex& self, int group) {
        self.group = group;
      });
mjsFlex.def_property("edgestiffness",[](raw::MjsFlex& self) -> double {
        return self.edgestiffness;
      },[](raw::MjsFlex& self, double edgestiffness) {
        self.edgestiffness = edgestiffness;
      });
mjsFlex.def_property("edgedamping",[](raw::MjsFlex& self) -> double {
        return self.edgedamping;
      },[](raw::MjsFlex& self, double edgedamping) {
        self.edgedamping = edgedamping;
      });
  mjsFlex.def_property(
      "rgba",
      [](raw::MjsFlex& self) -> MjFloat4 {
        return MjFloat4(self.rgba);
    },
      [](raw::MjsFlex& self, MjFloatRef4 rgba) {
        MjFloat4(self.rgba) = rgba;
    }, py::return_value_policy::reference_internal);
  mjsFlex.def_property(
      "material",
      [](raw::MjsFlex& self) -> std::string_view {
        return *self.material;
      },
      [](raw::MjsFlex& self, std::string_view material) {
        *(self.material) = material;
    });
  mjsFlex.def_property(
    "vertbody",
    [](raw::MjsFlex& self) -> py::list {
        py::list list;
        for (auto val : *self.vertbody) {
          list.append(val);
        }
        return list;
      },
    [](raw::MjsFlex& self, py::object rhs) {
        self.vertbody->clear();
        self.vertbody->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.vertbody->push_back(py::cast<std::string>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsFlex.def_property(
    "vert",
    [](raw::MjsFlex& self) -> py::array_t<double> {
        return py::array_t<double>(self.vert->size(),
                                      self.vert->data());
      },
    [](raw::MjsFlex& self, py::object rhs) {
        self.vert->clear();
        self.vert->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.vert->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsFlex.def_property(
    "elem",
    [](raw::MjsFlex& self) -> py::array_t<int> {
        return py::array_t<int>(self.elem->size(),
                                      self.elem->data());
      },
    [](raw::MjsFlex& self, py::object rhs) {
        self.elem->clear();
        self.elem->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.elem->push_back(py::cast<int>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsFlex.def_property(
    "texcoord",
    [](raw::MjsFlex& self) -> py::array_t<float> {
        return py::array_t<float>(self.texcoord->size(),
                                      self.texcoord->data());
      },
    [](raw::MjsFlex& self, py::object rhs) {
        self.texcoord->clear();
        self.texcoord->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.texcoord->push_back(py::cast<float>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsFlex.def_property(
      "info",
      [](raw::MjsFlex& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsFlex& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsMesh
  mjsMesh.def_property(
      "name",
      [](raw::MjsMesh& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsMesh& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsMesh.def_property(
      "content_type",
      [](raw::MjsMesh& self) -> std::string_view {
        return *self.content_type;
      },
      [](raw::MjsMesh& self, std::string_view content_type) {
        *(self.content_type) = content_type;
    });
  mjsMesh.def_property(
      "file",
      [](raw::MjsMesh& self) -> std::string_view {
        return *self.file;
      },
      [](raw::MjsMesh& self, std::string_view file) {
        *(self.file) = file;
    });
  mjsMesh.def_property(
      "refpos",
      [](raw::MjsMesh& self) -> MjDouble3 {
        return MjDouble3(self.refpos);
    },
      [](raw::MjsMesh& self, MjDoubleRef3 refpos) {
        MjDouble3(self.refpos) = refpos;
    }, py::return_value_policy::reference_internal);
  mjsMesh.def_property(
      "refquat",
      [](raw::MjsMesh& self) -> MjDouble4 {
        return MjDouble4(self.refquat);
    },
      [](raw::MjsMesh& self, MjDoubleRef4 refquat) {
        MjDouble4(self.refquat) = refquat;
    }, py::return_value_policy::reference_internal);
  mjsMesh.def_property(
      "scale",
      [](raw::MjsMesh& self) -> MjDouble3 {
        return MjDouble3(self.scale);
    },
      [](raw::MjsMesh& self, MjDoubleRef3 scale) {
        MjDouble3(self.scale) = scale;
    }, py::return_value_policy::reference_internal);
mjsMesh.def_property("smoothnormal",[](raw::MjsMesh& self) -> mjtByte {
        return self.smoothnormal;
      },[](raw::MjsMesh& self, mjtByte smoothnormal) {
        self.smoothnormal = smoothnormal;
      });
mjsMesh.def_property("maxhullvert",[](raw::MjsMesh& self) -> int {
        return self.maxhullvert;
      },[](raw::MjsMesh& self, int maxhullvert) {
        self.maxhullvert = maxhullvert;
      });
  mjsMesh.def_property(
    "uservert",
    [](raw::MjsMesh& self) -> py::array_t<float> {
        return py::array_t<float>(self.uservert->size(),
                                      self.uservert->data());
      },
    [](raw::MjsMesh& self, py::object rhs) {
        self.uservert->clear();
        self.uservert->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.uservert->push_back(py::cast<float>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsMesh.def_property(
    "usernormal",
    [](raw::MjsMesh& self) -> py::array_t<float> {
        return py::array_t<float>(self.usernormal->size(),
                                      self.usernormal->data());
      },
    [](raw::MjsMesh& self, py::object rhs) {
        self.usernormal->clear();
        self.usernormal->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.usernormal->push_back(py::cast<float>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsMesh.def_property(
    "usertexcoord",
    [](raw::MjsMesh& self) -> py::array_t<float> {
        return py::array_t<float>(self.usertexcoord->size(),
                                      self.usertexcoord->data());
      },
    [](raw::MjsMesh& self, py::object rhs) {
        self.usertexcoord->clear();
        self.usertexcoord->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.usertexcoord->push_back(py::cast<float>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsMesh.def_property(
    "userface",
    [](raw::MjsMesh& self) -> py::array_t<int> {
        return py::array_t<int>(self.userface->size(),
                                      self.userface->data());
      },
    [](raw::MjsMesh& self, py::object rhs) {
        self.userface->clear();
        self.userface->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.userface->push_back(py::cast<int>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsMesh.def_property(
    "userfacenormal",
    [](raw::MjsMesh& self) -> py::array_t<int> {
        return py::array_t<int>(self.userfacenormal->size(),
                                      self.userfacenormal->data());
      },
    [](raw::MjsMesh& self, py::object rhs) {
        self.userfacenormal->clear();
        self.userfacenormal->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.userfacenormal->push_back(py::cast<int>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsMesh.def_property(
    "userfacetexcoord",
    [](raw::MjsMesh& self) -> py::array_t<int> {
        return py::array_t<int>(self.userfacetexcoord->size(),
                                      self.userfacetexcoord->data());
      },
    [](raw::MjsMesh& self, py::object rhs) {
        self.userfacetexcoord->clear();
        self.userfacetexcoord->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.userfacetexcoord->push_back(py::cast<int>(val));
      }
    }, py::return_value_policy::reference_internal);
mjsMesh.def_property("plugin",[](raw::MjsMesh& self) -> raw::MjsPlugin {
        return self.plugin;
      },[](raw::MjsMesh& self, raw::MjsPlugin plugin) {
        self.plugin = plugin;
      },py::return_value_policy::reference_internal);
  mjsMesh.def_property(
      "info",
      [](raw::MjsMesh& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsMesh& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsHField
  mjsHField.def_property(
      "name",
      [](raw::MjsHField& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsHField& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsHField.def_property(
      "content_type",
      [](raw::MjsHField& self) -> std::string_view {
        return *self.content_type;
      },
      [](raw::MjsHField& self, std::string_view content_type) {
        *(self.content_type) = content_type;
    });
  mjsHField.def_property(
      "file",
      [](raw::MjsHField& self) -> std::string_view {
        return *self.file;
      },
      [](raw::MjsHField& self, std::string_view file) {
        *(self.file) = file;
    });
  mjsHField.def_property(
      "size",
      [](raw::MjsHField& self) -> MjDouble4 {
        return MjDouble4(self.size);
    },
      [](raw::MjsHField& self, MjDoubleRef4 size) {
        MjDouble4(self.size) = size;
    }, py::return_value_policy::reference_internal);
mjsHField.def_property("nrow",[](raw::MjsHField& self) -> int {
        return self.nrow;
      },[](raw::MjsHField& self, int nrow) {
        self.nrow = nrow;
      });
mjsHField.def_property("ncol",[](raw::MjsHField& self) -> int {
        return self.ncol;
      },[](raw::MjsHField& self, int ncol) {
        self.ncol = ncol;
      });
  mjsHField.def_property(
    "userdata",
    [](raw::MjsHField& self) -> py::array_t<float> {
        return py::array_t<float>(self.userdata->size(),
                                      self.userdata->data());
      },
    [](raw::MjsHField& self, py::object rhs) {
        self.userdata->clear();
        self.userdata->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.userdata->push_back(py::cast<float>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsHField.def_property(
      "info",
      [](raw::MjsHField& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsHField& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsSkin
  mjsSkin.def_property(
      "name",
      [](raw::MjsSkin& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsSkin& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsSkin.def_property(
      "file",
      [](raw::MjsSkin& self) -> std::string_view {
        return *self.file;
      },
      [](raw::MjsSkin& self, std::string_view file) {
        *(self.file) = file;
    });
  mjsSkin.def_property(
      "material",
      [](raw::MjsSkin& self) -> std::string_view {
        return *self.material;
      },
      [](raw::MjsSkin& self, std::string_view material) {
        *(self.material) = material;
    });
  mjsSkin.def_property(
      "rgba",
      [](raw::MjsSkin& self) -> MjFloat4 {
        return MjFloat4(self.rgba);
    },
      [](raw::MjsSkin& self, MjFloatRef4 rgba) {
        MjFloat4(self.rgba) = rgba;
    }, py::return_value_policy::reference_internal);
mjsSkin.def_property("inflate",[](raw::MjsSkin& self) -> float {
        return self.inflate;
      },[](raw::MjsSkin& self, float inflate) {
        self.inflate = inflate;
      });
mjsSkin.def_property("group",[](raw::MjsSkin& self) -> int {
        return self.group;
      },[](raw::MjsSkin& self, int group) {
        self.group = group;
      });
  mjsSkin.def_property(
    "vert",
    [](raw::MjsSkin& self) -> py::array_t<float> {
        return py::array_t<float>(self.vert->size(),
                                      self.vert->data());
      },
    [](raw::MjsSkin& self, py::object rhs) {
        self.vert->clear();
        self.vert->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.vert->push_back(py::cast<float>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsSkin.def_property(
    "texcoord",
    [](raw::MjsSkin& self) -> py::array_t<float> {
        return py::array_t<float>(self.texcoord->size(),
                                      self.texcoord->data());
      },
    [](raw::MjsSkin& self, py::object rhs) {
        self.texcoord->clear();
        self.texcoord->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.texcoord->push_back(py::cast<float>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsSkin.def_property(
    "face",
    [](raw::MjsSkin& self) -> py::array_t<int> {
        return py::array_t<int>(self.face->size(),
                                      self.face->data());
      },
    [](raw::MjsSkin& self, py::object rhs) {
        self.face->clear();
        self.face->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.face->push_back(py::cast<int>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsSkin.def_property(
    "bodyname",
    [](raw::MjsSkin& self) -> py::list {
        py::list list;
        for (auto val : *self.bodyname) {
          list.append(val);
        }
        return list;
      },
    [](raw::MjsSkin& self, py::object rhs) {
        self.bodyname->clear();
        self.bodyname->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.bodyname->push_back(py::cast<std::string>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsSkin.def_property(
    "bindpos",
    [](raw::MjsSkin& self) -> py::array_t<float> {
        return py::array_t<float>(self.bindpos->size(),
                                      self.bindpos->data());
      },
    [](raw::MjsSkin& self, py::object rhs) {
        self.bindpos->clear();
        self.bindpos->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.bindpos->push_back(py::cast<float>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsSkin.def_property(
    "bindquat",
    [](raw::MjsSkin& self) -> py::array_t<float> {
        return py::array_t<float>(self.bindquat->size(),
                                      self.bindquat->data());
      },
    [](raw::MjsSkin& self, py::object rhs) {
        self.bindquat->clear();
        self.bindquat->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.bindquat->push_back(py::cast<float>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsSkin.def_property(
    "vertid",
    [](raw::MjsSkin& self) -> py::list {
        py::list list;
        for (auto inner_vec : *self.vertid) {
          py::list inner_list;
          for (auto val : inner_vec) {
            inner_list.append(val);
          }
          list.append(inner_list);
        }
        return list;
      },
    [](raw::MjsSkin& self, py::object rhs) {
        self.vertid->clear();
        self.vertid->reserve(py::len(rhs));
        for (auto inner_list : rhs) {
          auto inner_vec = py::cast<std::vector<int>>(inner_list);
          self.vertid->push_back(inner_vec);
        }
    }, py::return_value_policy::reference_internal);
  mjsSkin.def_property(
    "vertweight",
    [](raw::MjsSkin& self) -> py::list {
        py::list list;
        for (auto inner_vec : *self.vertweight) {
          py::list inner_list;
          for (auto val : inner_vec) {
            inner_list.append(val);
          }
          list.append(inner_list);
        }
        return list;
      },
    [](raw::MjsSkin& self, py::object rhs) {
        self.vertweight->clear();
        self.vertweight->reserve(py::len(rhs));
        for (auto inner_list : rhs) {
          auto inner_vec = py::cast<std::vector<float>>(inner_list);
          self.vertweight->push_back(inner_vec);
        }
    }, py::return_value_policy::reference_internal);
  mjsSkin.def_property(
      "info",
      [](raw::MjsSkin& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsSkin& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsTexture
  mjsTexture.def_property(
      "name",
      [](raw::MjsTexture& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsTexture& self, std::string_view name) {
        *(self.name) = name;
    });
mjsTexture.def_property("type",[](raw::MjsTexture& self) -> mjtTexture& {
        return self.type;
      },[](raw::MjsTexture& self, mjtTexture& type) {
        self.type = type;
      },py::return_value_policy::reference_internal);
mjsTexture.def_property("builtin",[](raw::MjsTexture& self) -> int {
        return self.builtin;
      },[](raw::MjsTexture& self, int builtin) {
        self.builtin = builtin;
      });
mjsTexture.def_property("mark",[](raw::MjsTexture& self) -> int {
        return self.mark;
      },[](raw::MjsTexture& self, int mark) {
        self.mark = mark;
      });
  mjsTexture.def_property(
      "rgb1",
      [](raw::MjsTexture& self) -> MjDouble3 {
        return MjDouble3(self.rgb1);
    },
      [](raw::MjsTexture& self, MjDoubleRef3 rgb1) {
        MjDouble3(self.rgb1) = rgb1;
    }, py::return_value_policy::reference_internal);
  mjsTexture.def_property(
      "rgb2",
      [](raw::MjsTexture& self) -> MjDouble3 {
        return MjDouble3(self.rgb2);
    },
      [](raw::MjsTexture& self, MjDoubleRef3 rgb2) {
        MjDouble3(self.rgb2) = rgb2;
    }, py::return_value_policy::reference_internal);
  mjsTexture.def_property(
      "markrgb",
      [](raw::MjsTexture& self) -> MjDouble3 {
        return MjDouble3(self.markrgb);
    },
      [](raw::MjsTexture& self, MjDoubleRef3 markrgb) {
        MjDouble3(self.markrgb) = markrgb;
    }, py::return_value_policy::reference_internal);
mjsTexture.def_property("random",[](raw::MjsTexture& self) -> double {
        return self.random;
      },[](raw::MjsTexture& self, double random) {
        self.random = random;
      });
mjsTexture.def_property("height",[](raw::MjsTexture& self) -> int {
        return self.height;
      },[](raw::MjsTexture& self, int height) {
        self.height = height;
      });
mjsTexture.def_property("width",[](raw::MjsTexture& self) -> int {
        return self.width;
      },[](raw::MjsTexture& self, int width) {
        self.width = width;
      });
  mjsTexture.def_property(
      "content_type",
      [](raw::MjsTexture& self) -> std::string_view {
        return *self.content_type;
      },
      [](raw::MjsTexture& self, std::string_view content_type) {
        *(self.content_type) = content_type;
    });
  mjsTexture.def_property(
      "file",
      [](raw::MjsTexture& self) -> std::string_view {
        return *self.file;
      },
      [](raw::MjsTexture& self, std::string_view file) {
        *(self.file) = file;
    });
  mjsTexture.def_property(
      "gridsize",
      [](raw::MjsTexture& self) -> MjInt2 {
        return MjInt2(self.gridsize);
    },
      [](raw::MjsTexture& self, MjIntRef2 gridsize) {
        MjInt2(self.gridsize) = gridsize;
    }, py::return_value_policy::reference_internal);
  mjsTexture.def_property(
    "gridlayout",
    [](raw::MjsTexture& self) -> py::array_t<char> {
      return py::array_t<char>(13, self.gridlayout);
    },
    [](raw::MjsTexture& self, py::object rhs) {
      int i = 0;
      for (auto val : rhs) {
        self.gridlayout[i++] = py::cast<char>(val);
      }
    }, py::return_value_policy::reference_internal);
  mjsTexture.def_property(
    "cubefiles",
    [](raw::MjsTexture& self) -> py::list {
        py::list list;
        for (auto val : *self.cubefiles) {
          list.append(val);
        }
        return list;
      },
    [](raw::MjsTexture& self, py::object rhs) {
        self.cubefiles->clear();
        self.cubefiles->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.cubefiles->push_back(py::cast<std::string>(val));
      }
    }, py::return_value_policy::reference_internal);
mjsTexture.def_property("hflip",[](raw::MjsTexture& self) -> mjtByte {
        return self.hflip;
      },[](raw::MjsTexture& self, mjtByte hflip) {
        self.hflip = hflip;
      });
mjsTexture.def_property("vflip",[](raw::MjsTexture& self) -> mjtByte {
        return self.vflip;
      },[](raw::MjsTexture& self, mjtByte vflip) {
        self.vflip = vflip;
      });
  mjsTexture.def_property(
      "info",
      [](raw::MjsTexture& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsTexture& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsMaterial
  mjsMaterial.def_property(
      "name",
      [](raw::MjsMaterial& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsMaterial& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsMaterial.def_property(
      "texture",
      [](raw::MjsMaterial& self) -> std::string_view {
        return *self.texture;
      },
      [](raw::MjsMaterial& self, std::string_view texture) {
        *(self.texture) = texture;
    });
mjsMaterial.def_property("texuniform",[](raw::MjsMaterial& self) -> mjtByte {
        return self.texuniform;
      },[](raw::MjsMaterial& self, mjtByte texuniform) {
        self.texuniform = texuniform;
      });
  mjsMaterial.def_property(
      "texrepeat",
      [](raw::MjsMaterial& self) -> MjFloat2 {
        return MjFloat2(self.texrepeat);
    },
      [](raw::MjsMaterial& self, MjFloatRef2 texrepeat) {
        MjFloat2(self.texrepeat) = texrepeat;
    }, py::return_value_policy::reference_internal);
mjsMaterial.def_property("emission",[](raw::MjsMaterial& self) -> float {
        return self.emission;
      },[](raw::MjsMaterial& self, float emission) {
        self.emission = emission;
      });
mjsMaterial.def_property("specular",[](raw::MjsMaterial& self) -> float {
        return self.specular;
      },[](raw::MjsMaterial& self, float specular) {
        self.specular = specular;
      });
mjsMaterial.def_property("shininess",[](raw::MjsMaterial& self) -> float {
        return self.shininess;
      },[](raw::MjsMaterial& self, float shininess) {
        self.shininess = shininess;
      });
mjsMaterial.def_property("reflectance",[](raw::MjsMaterial& self) -> float {
        return self.reflectance;
      },[](raw::MjsMaterial& self, float reflectance) {
        self.reflectance = reflectance;
      });
mjsMaterial.def_property("metallic",[](raw::MjsMaterial& self) -> float {
        return self.metallic;
      },[](raw::MjsMaterial& self, float metallic) {
        self.metallic = metallic;
      });
mjsMaterial.def_property("roughness",[](raw::MjsMaterial& self) -> float {
        return self.roughness;
      },[](raw::MjsMaterial& self, float roughness) {
        self.roughness = roughness;
      });
  mjsMaterial.def_property(
      "rgba",
      [](raw::MjsMaterial& self) -> MjFloat4 {
        return MjFloat4(self.rgba);
    },
      [](raw::MjsMaterial& self, MjFloatRef4 rgba) {
        MjFloat4(self.rgba) = rgba;
    }, py::return_value_policy::reference_internal);
  mjsMaterial.def_property(
      "info",
      [](raw::MjsMaterial& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsMaterial& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsPair
  mjsPair.def_property(
      "name",
      [](raw::MjsPair& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsPair& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsPair.def_property(
      "geomname1",
      [](raw::MjsPair& self) -> std::string_view {
        return *self.geomname1;
      },
      [](raw::MjsPair& self, std::string_view geomname1) {
        *(self.geomname1) = geomname1;
    });
  mjsPair.def_property(
      "geomname2",
      [](raw::MjsPair& self) -> std::string_view {
        return *self.geomname2;
      },
      [](raw::MjsPair& self, std::string_view geomname2) {
        *(self.geomname2) = geomname2;
    });
mjsPair.def_property("condim",[](raw::MjsPair& self) -> int {
        return self.condim;
      },[](raw::MjsPair& self, int condim) {
        self.condim = condim;
      });
  mjsPair.def_property(
      "solref",
      [](raw::MjsPair& self) -> MjDouble2 {
        return MjDouble2(self.solref);
    },
      [](raw::MjsPair& self, MjDoubleRef2 solref) {
        MjDouble2(self.solref) = solref;
    }, py::return_value_policy::reference_internal);
  mjsPair.def_property(
      "solreffriction",
      [](raw::MjsPair& self) -> MjDouble2 {
        return MjDouble2(self.solreffriction);
    },
      [](raw::MjsPair& self, MjDoubleRef2 solreffriction) {
        MjDouble2(self.solreffriction) = solreffriction;
    }, py::return_value_policy::reference_internal);
  mjsPair.def_property(
      "solimp",
      [](raw::MjsPair& self) -> MjDouble5 {
        return MjDouble5(self.solimp);
    },
      [](raw::MjsPair& self, MjDoubleRef5 solimp) {
        MjDouble5(self.solimp) = solimp;
    }, py::return_value_policy::reference_internal);
mjsPair.def_property("margin",[](raw::MjsPair& self) -> double {
        return self.margin;
      },[](raw::MjsPair& self, double margin) {
        self.margin = margin;
      });
mjsPair.def_property("gap",[](raw::MjsPair& self) -> double {
        return self.gap;
      },[](raw::MjsPair& self, double gap) {
        self.gap = gap;
      });
  mjsPair.def_property(
      "friction",
      [](raw::MjsPair& self) -> MjDouble5 {
        return MjDouble5(self.friction);
    },
      [](raw::MjsPair& self, MjDoubleRef5 friction) {
        MjDouble5(self.friction) = friction;
    }, py::return_value_policy::reference_internal);
  mjsPair.def_property(
      "info",
      [](raw::MjsPair& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsPair& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsExclude
  mjsExclude.def_property(
      "name",
      [](raw::MjsExclude& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsExclude& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsExclude.def_property(
      "bodyname1",
      [](raw::MjsExclude& self) -> std::string_view {
        return *self.bodyname1;
      },
      [](raw::MjsExclude& self, std::string_view bodyname1) {
        *(self.bodyname1) = bodyname1;
    });
  mjsExclude.def_property(
      "bodyname2",
      [](raw::MjsExclude& self) -> std::string_view {
        return *self.bodyname2;
      },
      [](raw::MjsExclude& self, std::string_view bodyname2) {
        *(self.bodyname2) = bodyname2;
    });
  mjsExclude.def_property(
      "info",
      [](raw::MjsExclude& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsExclude& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsEquality
  mjsEquality.def_property(
      "name",
      [](raw::MjsEquality& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsEquality& self, std::string_view name) {
        *(self.name) = name;
    });
mjsEquality.def_property("type",[](raw::MjsEquality& self) -> mjtEq& {
        return self.type;
      },[](raw::MjsEquality& self, mjtEq& type) {
        self.type = type;
      },py::return_value_policy::reference_internal);
  mjsEquality.def_property(
      "data",
      [](raw::MjsEquality& self) -> MjDouble11 {
        return MjDouble11(self.data);
    },
      [](raw::MjsEquality& self, MjDoubleRef11 data) {
        MjDouble11(self.data) = data;
    }, py::return_value_policy::reference_internal);
mjsEquality.def_property("active",[](raw::MjsEquality& self) -> mjtByte {
        return self.active;
      },[](raw::MjsEquality& self, mjtByte active) {
        self.active = active;
      });
  mjsEquality.def_property(
      "name1",
      [](raw::MjsEquality& self) -> std::string_view {
        return *self.name1;
      },
      [](raw::MjsEquality& self, std::string_view name1) {
        *(self.name1) = name1;
    });
  mjsEquality.def_property(
      "name2",
      [](raw::MjsEquality& self) -> std::string_view {
        return *self.name2;
      },
      [](raw::MjsEquality& self, std::string_view name2) {
        *(self.name2) = name2;
    });
  mjsEquality.def_property(
      "solref",
      [](raw::MjsEquality& self) -> MjDouble2 {
        return MjDouble2(self.solref);
    },
      [](raw::MjsEquality& self, MjDoubleRef2 solref) {
        MjDouble2(self.solref) = solref;
    }, py::return_value_policy::reference_internal);
  mjsEquality.def_property(
      "solimp",
      [](raw::MjsEquality& self) -> MjDouble5 {
        return MjDouble5(self.solimp);
    },
      [](raw::MjsEquality& self, MjDoubleRef5 solimp) {
        MjDouble5(self.solimp) = solimp;
    }, py::return_value_policy::reference_internal);
  mjsEquality.def_property(
      "info",
      [](raw::MjsEquality& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsEquality& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsTendon
  mjsTendon.def_property(
      "name",
      [](raw::MjsTendon& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsTendon& self, std::string_view name) {
        *(self.name) = name;
    });
mjsTendon.def_property("stiffness",[](raw::MjsTendon& self) -> double {
        return self.stiffness;
      },[](raw::MjsTendon& self, double stiffness) {
        self.stiffness = stiffness;
      });
  mjsTendon.def_property(
      "springlength",
      [](raw::MjsTendon& self) -> MjDouble2 {
        return MjDouble2(self.springlength);
    },
      [](raw::MjsTendon& self, MjDoubleRef2 springlength) {
        MjDouble2(self.springlength) = springlength;
    }, py::return_value_policy::reference_internal);
mjsTendon.def_property("damping",[](raw::MjsTendon& self) -> double {
        return self.damping;
      },[](raw::MjsTendon& self, double damping) {
        self.damping = damping;
      });
mjsTendon.def_property("frictionloss",[](raw::MjsTendon& self) -> double {
        return self.frictionloss;
      },[](raw::MjsTendon& self, double frictionloss) {
        self.frictionloss = frictionloss;
      });
  mjsTendon.def_property(
      "solref_friction",
      [](raw::MjsTendon& self) -> MjDouble2 {
        return MjDouble2(self.solref_friction);
    },
      [](raw::MjsTendon& self, MjDoubleRef2 solref_friction) {
        MjDouble2(self.solref_friction) = solref_friction;
    }, py::return_value_policy::reference_internal);
  mjsTendon.def_property(
      "solimp_friction",
      [](raw::MjsTendon& self) -> MjDouble5 {
        return MjDouble5(self.solimp_friction);
    },
      [](raw::MjsTendon& self, MjDoubleRef5 solimp_friction) {
        MjDouble5(self.solimp_friction) = solimp_friction;
    }, py::return_value_policy::reference_internal);
mjsTendon.def_property("limited",[](raw::MjsTendon& self) -> int {
        return self.limited;
      },[](raw::MjsTendon& self, int limited) {
        self.limited = limited;
      });
  mjsTendon.def_property(
      "range",
      [](raw::MjsTendon& self) -> MjDouble2 {
        return MjDouble2(self.range);
    },
      [](raw::MjsTendon& self, MjDoubleRef2 range) {
        MjDouble2(self.range) = range;
    }, py::return_value_policy::reference_internal);
mjsTendon.def_property("margin",[](raw::MjsTendon& self) -> double {
        return self.margin;
      },[](raw::MjsTendon& self, double margin) {
        self.margin = margin;
      });
  mjsTendon.def_property(
      "solref_limit",
      [](raw::MjsTendon& self) -> MjDouble2 {
        return MjDouble2(self.solref_limit);
    },
      [](raw::MjsTendon& self, MjDoubleRef2 solref_limit) {
        MjDouble2(self.solref_limit) = solref_limit;
    }, py::return_value_policy::reference_internal);
  mjsTendon.def_property(
      "solimp_limit",
      [](raw::MjsTendon& self) -> MjDouble5 {
        return MjDouble5(self.solimp_limit);
    },
      [](raw::MjsTendon& self, MjDoubleRef5 solimp_limit) {
        MjDouble5(self.solimp_limit) = solimp_limit;
    }, py::return_value_policy::reference_internal);
  mjsTendon.def_property(
      "material",
      [](raw::MjsTendon& self) -> std::string_view {
        return *self.material;
      },
      [](raw::MjsTendon& self, std::string_view material) {
        *(self.material) = material;
    });
mjsTendon.def_property("width",[](raw::MjsTendon& self) -> double {
        return self.width;
      },[](raw::MjsTendon& self, double width) {
        self.width = width;
      });
  mjsTendon.def_property(
      "rgba",
      [](raw::MjsTendon& self) -> MjFloat4 {
        return MjFloat4(self.rgba);
    },
      [](raw::MjsTendon& self, MjFloatRef4 rgba) {
        MjFloat4(self.rgba) = rgba;
    }, py::return_value_policy::reference_internal);
mjsTendon.def_property("group",[](raw::MjsTendon& self) -> int {
        return self.group;
      },[](raw::MjsTendon& self, int group) {
        self.group = group;
      });
  mjsTendon.def_property(
    "userdata",
    [](raw::MjsTendon& self) -> py::array_t<double> {
        return py::array_t<double>(self.userdata->size(),
                                      self.userdata->data());
      },
    [](raw::MjsTendon& self, py::object rhs) {
        self.userdata->clear();
        self.userdata->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.userdata->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsTendon.def_property(
      "info",
      [](raw::MjsTendon& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsTendon& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsWrap
  mjsWrap.def_property(
      "info",
      [](raw::MjsWrap& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsWrap& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsActuator
  mjsActuator.def_property(
      "name",
      [](raw::MjsActuator& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsActuator& self, std::string_view name) {
        *(self.name) = name;
    });
mjsActuator.def_property("gaintype",[](raw::MjsActuator& self) -> mjtGain& {
        return self.gaintype;
      },[](raw::MjsActuator& self, mjtGain& gaintype) {
        self.gaintype = gaintype;
      },py::return_value_policy::reference_internal);
  mjsActuator.def_property(
      "gainprm",
      [](raw::MjsActuator& self) -> MjDouble10 {
        return MjDouble10(self.gainprm);
    },
      [](raw::MjsActuator& self, MjDoubleRef10 gainprm) {
        MjDouble10(self.gainprm) = gainprm;
    }, py::return_value_policy::reference_internal);
mjsActuator.def_property("biastype",[](raw::MjsActuator& self) -> mjtBias& {
        return self.biastype;
      },[](raw::MjsActuator& self, mjtBias& biastype) {
        self.biastype = biastype;
      },py::return_value_policy::reference_internal);
  mjsActuator.def_property(
      "biasprm",
      [](raw::MjsActuator& self) -> MjDouble10 {
        return MjDouble10(self.biasprm);
    },
      [](raw::MjsActuator& self, MjDoubleRef10 biasprm) {
        MjDouble10(self.biasprm) = biasprm;
    }, py::return_value_policy::reference_internal);
mjsActuator.def_property("dyntype",[](raw::MjsActuator& self) -> mjtDyn& {
        return self.dyntype;
      },[](raw::MjsActuator& self, mjtDyn& dyntype) {
        self.dyntype = dyntype;
      },py::return_value_policy::reference_internal);
  mjsActuator.def_property(
      "dynprm",
      [](raw::MjsActuator& self) -> MjDouble10 {
        return MjDouble10(self.dynprm);
    },
      [](raw::MjsActuator& self, MjDoubleRef10 dynprm) {
        MjDouble10(self.dynprm) = dynprm;
    }, py::return_value_policy::reference_internal);
mjsActuator.def_property("actdim",[](raw::MjsActuator& self) -> int {
        return self.actdim;
      },[](raw::MjsActuator& self, int actdim) {
        self.actdim = actdim;
      });
mjsActuator.def_property("actearly",[](raw::MjsActuator& self) -> mjtByte {
        return self.actearly;
      },[](raw::MjsActuator& self, mjtByte actearly) {
        self.actearly = actearly;
      });
mjsActuator.def_property("trntype",[](raw::MjsActuator& self) -> mjtTrn& {
        return self.trntype;
      },[](raw::MjsActuator& self, mjtTrn& trntype) {
        self.trntype = trntype;
      },py::return_value_policy::reference_internal);
  mjsActuator.def_property(
      "gear",
      [](raw::MjsActuator& self) -> MjDouble6 {
        return MjDouble6(self.gear);
    },
      [](raw::MjsActuator& self, MjDoubleRef6 gear) {
        MjDouble6(self.gear) = gear;
    }, py::return_value_policy::reference_internal);
  mjsActuator.def_property(
      "target",
      [](raw::MjsActuator& self) -> std::string_view {
        return *self.target;
      },
      [](raw::MjsActuator& self, std::string_view target) {
        *(self.target) = target;
    });
  mjsActuator.def_property(
      "refsite",
      [](raw::MjsActuator& self) -> std::string_view {
        return *self.refsite;
      },
      [](raw::MjsActuator& self, std::string_view refsite) {
        *(self.refsite) = refsite;
    });
  mjsActuator.def_property(
      "slidersite",
      [](raw::MjsActuator& self) -> std::string_view {
        return *self.slidersite;
      },
      [](raw::MjsActuator& self, std::string_view slidersite) {
        *(self.slidersite) = slidersite;
    });
mjsActuator.def_property("cranklength",[](raw::MjsActuator& self) -> double {
        return self.cranklength;
      },[](raw::MjsActuator& self, double cranklength) {
        self.cranklength = cranklength;
      });
  mjsActuator.def_property(
      "lengthrange",
      [](raw::MjsActuator& self) -> MjDouble2 {
        return MjDouble2(self.lengthrange);
    },
      [](raw::MjsActuator& self, MjDoubleRef2 lengthrange) {
        MjDouble2(self.lengthrange) = lengthrange;
    }, py::return_value_policy::reference_internal);
mjsActuator.def_property("inheritrange",[](raw::MjsActuator& self) -> double {
        return self.inheritrange;
      },[](raw::MjsActuator& self, double inheritrange) {
        self.inheritrange = inheritrange;
      });
mjsActuator.def_property("ctrllimited",[](raw::MjsActuator& self) -> int {
        return self.ctrllimited;
      },[](raw::MjsActuator& self, int ctrllimited) {
        self.ctrllimited = ctrllimited;
      });
  mjsActuator.def_property(
      "ctrlrange",
      [](raw::MjsActuator& self) -> MjDouble2 {
        return MjDouble2(self.ctrlrange);
    },
      [](raw::MjsActuator& self, MjDoubleRef2 ctrlrange) {
        MjDouble2(self.ctrlrange) = ctrlrange;
    }, py::return_value_policy::reference_internal);
mjsActuator.def_property("forcelimited",[](raw::MjsActuator& self) -> int {
        return self.forcelimited;
      },[](raw::MjsActuator& self, int forcelimited) {
        self.forcelimited = forcelimited;
      });
  mjsActuator.def_property(
      "forcerange",
      [](raw::MjsActuator& self) -> MjDouble2 {
        return MjDouble2(self.forcerange);
    },
      [](raw::MjsActuator& self, MjDoubleRef2 forcerange) {
        MjDouble2(self.forcerange) = forcerange;
    }, py::return_value_policy::reference_internal);
mjsActuator.def_property("actlimited",[](raw::MjsActuator& self) -> int {
        return self.actlimited;
      },[](raw::MjsActuator& self, int actlimited) {
        self.actlimited = actlimited;
      });
  mjsActuator.def_property(
      "actrange",
      [](raw::MjsActuator& self) -> MjDouble2 {
        return MjDouble2(self.actrange);
    },
      [](raw::MjsActuator& self, MjDoubleRef2 actrange) {
        MjDouble2(self.actrange) = actrange;
    }, py::return_value_policy::reference_internal);
mjsActuator.def_property("group",[](raw::MjsActuator& self) -> int {
        return self.group;
      },[](raw::MjsActuator& self, int group) {
        self.group = group;
      });
  mjsActuator.def_property(
    "userdata",
    [](raw::MjsActuator& self) -> py::array_t<double> {
        return py::array_t<double>(self.userdata->size(),
                                      self.userdata->data());
      },
    [](raw::MjsActuator& self, py::object rhs) {
        self.userdata->clear();
        self.userdata->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.userdata->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
mjsActuator.def_property("plugin",[](raw::MjsActuator& self) -> raw::MjsPlugin {
        return self.plugin;
      },[](raw::MjsActuator& self, raw::MjsPlugin plugin) {
        self.plugin = plugin;
      },py::return_value_policy::reference_internal);
  mjsActuator.def_property(
      "info",
      [](raw::MjsActuator& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsActuator& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsSensor
  mjsSensor.def_property(
      "name",
      [](raw::MjsSensor& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsSensor& self, std::string_view name) {
        *(self.name) = name;
    });
mjsSensor.def_property("type",[](raw::MjsSensor& self) -> mjtSensor& {
        return self.type;
      },[](raw::MjsSensor& self, mjtSensor& type) {
        self.type = type;
      },py::return_value_policy::reference_internal);
mjsSensor.def_property("objtype",[](raw::MjsSensor& self) -> mjtObj& {
        return self.objtype;
      },[](raw::MjsSensor& self, mjtObj& objtype) {
        self.objtype = objtype;
      },py::return_value_policy::reference_internal);
  mjsSensor.def_property(
      "objname",
      [](raw::MjsSensor& self) -> std::string_view {
        return *self.objname;
      },
      [](raw::MjsSensor& self, std::string_view objname) {
        *(self.objname) = objname;
    });
mjsSensor.def_property("reftype",[](raw::MjsSensor& self) -> mjtObj& {
        return self.reftype;
      },[](raw::MjsSensor& self, mjtObj& reftype) {
        self.reftype = reftype;
      },py::return_value_policy::reference_internal);
  mjsSensor.def_property(
      "refname",
      [](raw::MjsSensor& self) -> std::string_view {
        return *self.refname;
      },
      [](raw::MjsSensor& self, std::string_view refname) {
        *(self.refname) = refname;
    });
mjsSensor.def_property("datatype",[](raw::MjsSensor& self) -> mjtDataType& {
        return self.datatype;
      },[](raw::MjsSensor& self, mjtDataType& datatype) {
        self.datatype = datatype;
      },py::return_value_policy::reference_internal);
mjsSensor.def_property("needstage",[](raw::MjsSensor& self) -> mjtStage& {
        return self.needstage;
      },[](raw::MjsSensor& self, mjtStage& needstage) {
        self.needstage = needstage;
      },py::return_value_policy::reference_internal);
mjsSensor.def_property("dim",[](raw::MjsSensor& self) -> int {
        return self.dim;
      },[](raw::MjsSensor& self, int dim) {
        self.dim = dim;
      });
mjsSensor.def_property("cutoff",[](raw::MjsSensor& self) -> double {
        return self.cutoff;
      },[](raw::MjsSensor& self, double cutoff) {
        self.cutoff = cutoff;
      });
mjsSensor.def_property("noise",[](raw::MjsSensor& self) -> double {
        return self.noise;
      },[](raw::MjsSensor& self, double noise) {
        self.noise = noise;
      });
  mjsSensor.def_property(
    "userdata",
    [](raw::MjsSensor& self) -> py::array_t<double> {
        return py::array_t<double>(self.userdata->size(),
                                      self.userdata->data());
      },
    [](raw::MjsSensor& self, py::object rhs) {
        self.userdata->clear();
        self.userdata->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.userdata->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
mjsSensor.def_property("plugin",[](raw::MjsSensor& self) -> raw::MjsPlugin {
        return self.plugin;
      },[](raw::MjsSensor& self, raw::MjsPlugin plugin) {
        self.plugin = plugin;
      },py::return_value_policy::reference_internal);
  mjsSensor.def_property(
      "info",
      [](raw::MjsSensor& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsSensor& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsNumeric
  mjsNumeric.def_property(
      "name",
      [](raw::MjsNumeric& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsNumeric& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsNumeric.def_property(
    "data",
    [](raw::MjsNumeric& self) -> py::array_t<double> {
        return py::array_t<double>(self.data->size(),
                                      self.data->data());
      },
    [](raw::MjsNumeric& self, py::object rhs) {
        self.data->clear();
        self.data->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.data->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
mjsNumeric.def_property("size",[](raw::MjsNumeric& self) -> int {
        return self.size;
      },[](raw::MjsNumeric& self, int size) {
        self.size = size;
      });
  mjsNumeric.def_property(
      "info",
      [](raw::MjsNumeric& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsNumeric& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsText
  mjsText.def_property(
      "name",
      [](raw::MjsText& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsText& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsText.def_property(
      "data",
      [](raw::MjsText& self) -> std::string_view {
        return *self.data;
      },
      [](raw::MjsText& self, std::string_view data) {
        *(self.data) = data;
    });
  mjsText.def_property(
      "info",
      [](raw::MjsText& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsText& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsTuple
  mjsTuple.def_property(
      "name",
      [](raw::MjsTuple& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsTuple& self, std::string_view name) {
        *(self.name) = name;
    });
  mjsTuple.def_property(
    "objtype",
    [](raw::MjsTuple& self) -> py::array_t<int> {
        return py::array_t<int>(self.objtype->size(),
                                      self.objtype->data());
      },
    [](raw::MjsTuple& self, py::object rhs) {
        self.objtype->clear();
        self.objtype->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.objtype->push_back(py::cast<int>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsTuple.def_property(
    "objname",
    [](raw::MjsTuple& self) -> py::list {
        py::list list;
        for (auto val : *self.objname) {
          list.append(val);
        }
        return list;
      },
    [](raw::MjsTuple& self, py::object rhs) {
        self.objname->clear();
        self.objname->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.objname->push_back(py::cast<std::string>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsTuple.def_property(
    "objprm",
    [](raw::MjsTuple& self) -> py::array_t<double> {
        return py::array_t<double>(self.objprm->size(),
                                      self.objprm->data());
      },
    [](raw::MjsTuple& self, py::object rhs) {
        self.objprm->clear();
        self.objprm->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.objprm->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsTuple.def_property(
      "info",
      [](raw::MjsTuple& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsTuple& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsKey
  mjsKey.def_property(
      "name",
      [](raw::MjsKey& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsKey& self, std::string_view name) {
        *(self.name) = name;
    });
mjsKey.def_property("time",[](raw::MjsKey& self) -> double {
        return self.time;
      },[](raw::MjsKey& self, double time) {
        self.time = time;
      });
  mjsKey.def_property(
    "qpos",
    [](raw::MjsKey& self) -> py::array_t<double> {
        return py::array_t<double>(self.qpos->size(),
                                      self.qpos->data());
      },
    [](raw::MjsKey& self, py::object rhs) {
        self.qpos->clear();
        self.qpos->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.qpos->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsKey.def_property(
    "qvel",
    [](raw::MjsKey& self) -> py::array_t<double> {
        return py::array_t<double>(self.qvel->size(),
                                      self.qvel->data());
      },
    [](raw::MjsKey& self, py::object rhs) {
        self.qvel->clear();
        self.qvel->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.qvel->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsKey.def_property(
    "act",
    [](raw::MjsKey& self) -> py::array_t<double> {
        return py::array_t<double>(self.act->size(),
                                      self.act->data());
      },
    [](raw::MjsKey& self, py::object rhs) {
        self.act->clear();
        self.act->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.act->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsKey.def_property(
    "mpos",
    [](raw::MjsKey& self) -> py::array_t<double> {
        return py::array_t<double>(self.mpos->size(),
                                      self.mpos->data());
      },
    [](raw::MjsKey& self, py::object rhs) {
        self.mpos->clear();
        self.mpos->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.mpos->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsKey.def_property(
    "mquat",
    [](raw::MjsKey& self) -> py::array_t<double> {
        return py::array_t<double>(self.mquat->size(),
                                      self.mquat->data());
      },
    [](raw::MjsKey& self, py::object rhs) {
        self.mquat->clear();
        self.mquat->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.mquat->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsKey.def_property(
    "ctrl",
    [](raw::MjsKey& self) -> py::array_t<double> {
        return py::array_t<double>(self.ctrl->size(),
                                      self.ctrl->data());
      },
    [](raw::MjsKey& self, py::object rhs) {
        self.ctrl->clear();
        self.ctrl->reserve(py::len(rhs));
        for (auto val : rhs) {
          self.ctrl->push_back(py::cast<double>(val));
      }
    }, py::return_value_policy::reference_internal);
  mjsKey.def_property(
      "info",
      [](raw::MjsKey& self) -> std::string_view {
        return *self.info;
      },
      [](raw::MjsKey& self, std::string_view info) {
        *(self.info) = info;
    });

  // mjsDefault
  mjsDefault.def_property(
      "name",
      [](raw::MjsDefault& self) -> std::string_view {
        return *self.name;
      },
      [](raw::MjsDefault& self, std::string_view name) {
        *(self.name) = name;
    });
mjsDefault.def_property("joint",[](raw::MjsDefault& self) -> raw::MjsJoint* {
        return self.joint;
      },[](raw::MjsDefault& self, raw::MjsJoint* joint) {
        self.joint = joint;
      },py::return_value_policy::reference_internal);
mjsDefault.def_property("geom",[](raw::MjsDefault& self) -> raw::MjsGeom* {
        return self.geom;
      },[](raw::MjsDefault& self, raw::MjsGeom* geom) {
        self.geom = geom;
      },py::return_value_policy::reference_internal);
mjsDefault.def_property("site",[](raw::MjsDefault& self) -> raw::MjsSite* {
        return self.site;
      },[](raw::MjsDefault& self, raw::MjsSite* site) {
        self.site = site;
      },py::return_value_policy::reference_internal);
mjsDefault.def_property("camera",[](raw::MjsDefault& self) -> raw::MjsCamera* {
        return self.camera;
      },[](raw::MjsDefault& self, raw::MjsCamera* camera) {
        self.camera = camera;
      },py::return_value_policy::reference_internal);
mjsDefault.def_property("light",[](raw::MjsDefault& self) -> raw::MjsLight* {
        return self.light;
      },[](raw::MjsDefault& self, raw::MjsLight* light) {
        self.light = light;
      },py::return_value_policy::reference_internal);
mjsDefault.def_property("flex",[](raw::MjsDefault& self) -> raw::MjsFlex* {
        return self.flex;
      },[](raw::MjsDefault& self, raw::MjsFlex* flex) {
        self.flex = flex;
      },py::return_value_policy::reference_internal);
mjsDefault.def_property("mesh",[](raw::MjsDefault& self) -> raw::MjsMesh* {
        return self.mesh;
      },[](raw::MjsDefault& self, raw::MjsMesh* mesh) {
        self.mesh = mesh;
      },py::return_value_policy::reference_internal);
mjsDefault.def_property("material",[](raw::MjsDefault& self) -> raw::MjsMaterial* {
        return self.material;
      },[](raw::MjsDefault& self, raw::MjsMaterial* material) {
        self.material = material;
      },py::return_value_policy::reference_internal);
mjsDefault.def_property("pair",[](raw::MjsDefault& self) -> raw::MjsPair* {
        return self.pair;
      },[](raw::MjsDefault& self, raw::MjsPair* pair) {
        self.pair = pair;
      },py::return_value_policy::reference_internal);
mjsDefault.def_property("equality",[](raw::MjsDefault& self) -> raw::MjsEquality* {
        return self.equality;
      },[](raw::MjsDefault& self, raw::MjsEquality* equality) {
        self.equality = equality;
      },py::return_value_policy::reference_internal);
mjsDefault.def_property("tendon",[](raw::MjsDefault& self) -> raw::MjsTendon* {
        return self.tendon;
      },[](raw::MjsDefault& self, raw::MjsTendon* tendon) {
        self.tendon = tendon;
      },py::return_value_policy::reference_internal);
mjsDefault.def_property("actuator",[](raw::MjsDefault& self) -> raw::MjsActuator* {
        return self.actuator;
      },[](raw::MjsDefault& self, raw::MjsActuator* actuator) {
        self.actuator = actuator;
      },py::return_value_policy::reference_internal);
